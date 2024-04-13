import streamlit as st
import pandas as pd
import os
from typing import Optional, List, Tuple, Set
from presidio_analyzer import (
    RecognizerResult,
    EntityRecognizer,
    AnalysisExplanation,
    AnalyzerEngine,
    RecognizerRegistry,
    Pattern,
    PatternRecognizer,
    predefined_recognizers,
)
from presidio_analyzer.nlp_engine import (
    NlpArtifacts,
    NlpEngineProvider,
)
from presidio_anonymizer import AnonymizerEngine

try:
    from flair.data import Sentence
    from flair.models import SequenceTagger
except ImportError:
    print("Flair is not installed")

from helper import get_hostname
from tools.tool_base import ToolBase, DEV_WORKSTATIONS

DEMO_FILENAME = "./data/demo/rapport_4721-b.txt"


class FlairRecognizer(EntityRecognizer):
    """
    Wrapper for a flair model, if needed to be used within Presidio Analyzer.

    :example:
    >from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

    >flair_recognizer = FlairRecognizer()

    >registry = RecognizerRegistry()
    >registry.add_recognizer(flair_recognizer)

    >analyzer = AnalyzerEngine(registry=registry)

    >results = analyzer.analyze(
    >    "My name is Christopher and I live in Irbid.",
    >    language="en",
    >    return_decision_process=True,
    >)
    >for result in results:
    >    print(result)
    >    print(result.analysis_explanation)


    """

    ENTITIES = [
        "LOCATION",
        "PERSON",
        "ORGANIZATION",
        #    "MISCELLANEOUS",   # - There are no direct correlation with Presidio entities.
    ]

    DEFAULT_EXPLANATION = "Identified as {} by Flair's Named Entity Recognition"

    CHECK_LABEL_GROUPS = [
        ({"LOCATION"}, {"LOC", "LOCATION"}),
        ({"PERSON"}, {"PER", "PERSON"}),
        ({"ORGANIZATION"}, {"ORG"}),
        #    ({"MISCELLANEOUS"}, {"MISC"}), # Probably not PII
    ]

    MODEL_LANGUAGES = {
        # "en": "flair/ner-english-large",
        "de": "flair/ner-german-large",
    }

    PRESIDIO_EQUIVALENCES = {
        "PER": "PERSON",
        "LOC": "LOCATION",
        "ORG": "ORGANIZATION",
        # 'MISC': 'MISCELLANEOUS'   # - Probably not PII
    }

    def __init__(
        self,
        supported_language: str = "en",
        supported_entities: Optional[List[str]] = None,
        check_label_groups: Optional[Tuple[Set, Set]] = None,
        model: SequenceTagger = None,
    ):
        self.check_label_groups = (
            check_label_groups if check_label_groups else self.CHECK_LABEL_GROUPS
        )

        supported_entities = supported_entities if supported_entities else self.ENTITIES
        self.model = (
            model
            if model
            else SequenceTagger.load(self.MODEL_LANGUAGES.get(supported_language))
            # else SequenceTagger.load("flair/ner-german")
        )

        super().__init__(
            supported_entities=supported_entities,
            supported_language=supported_language,
            name="Flair Analytics",
        )

    def load(self) -> None:
        """Load the model, not used. Model is loaded during initialization."""
        pass

    def get_supported_entities(self) -> List[str]:
        """
        Return supported entities by this model.

        :return: List of the supported entities.
        """
        return self.supported_entities

    # Class to use Flair with Presidio as an external recognizer.
    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts = None
    ) -> List[RecognizerResult]:
        """
        Analyze text using Text Analytics.

        :param text: The text for analysis.
        :param entities: Not working properly for this recognizer.
        :param nlp_artifacts: Not used by this recognizer.
        :param language: Text language. Supported languages in MODEL_LANGUAGES
        :return: The list of Presidio RecognizerResult constructed from the recognized
            Flair detections.
        """

        results = []

        sentences = Sentence(text)
        self.model.predict(sentences)

        # If there are no specific list of entities, we will look for all of it.
        if not entities:
            entities = self.supported_entities

        for entity in entities:
            if entity not in self.supported_entities:
                continue

            for ent in sentences.get_spans("ner"):
                if not self.__check_label(
                    entity, ent.labels[0].value, self.check_label_groups
                ):
                    continue
                textual_explanation = self.DEFAULT_EXPLANATION.format(
                    ent.labels[0].value
                )
                explanation = self.build_flair_explanation(
                    round(ent.score, 2), textual_explanation
                )
                flair_result = self._convert_to_recognizer_result(ent, explanation)

                results.append(flair_result)

        return results

    def _convert_to_recognizer_result(self, entity, explanation) -> RecognizerResult:
        entity_type = self.PRESIDIO_EQUIVALENCES.get(entity.tag, entity.tag)
        flair_score = round(entity.score, 2)

        flair_results = RecognizerResult(
            entity_type=entity_type,
            start=entity.start_position,
            end=entity.end_position,
            score=flair_score,
            analysis_explanation=explanation,
        )

        return flair_results

    def build_flair_explanation(
        self, original_score: float, explanation: str
    ) -> AnalysisExplanation:
        """
        Create explanation for why this result was detected.

        :param original_score: Score given by this recognizer
        :param explanation: Explanation string
        :return:
        """
        explanation = AnalysisExplanation(
            recognizer=self.__class__.__name__,
            original_score=original_score,
            textual_explanation=explanation,
        )
        return explanation

    @staticmethod
    def __check_label(
        entity: str, label: str, check_label_groups: Tuple[Set, Set]
    ) -> bool:
        return any(
            [entity in egrp and label in lgrp for egrp, lgrp in check_label_groups]
        )


class Anonymizer(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.title = "Anonymisierung"
        self.texts_df = pd.DataFrame()
        self.formats = [
            "Demo",
            "csv-Datai",
            "json-Datei",
            "Dokumentensammlung txt (gezippt)",
        ]
        self.separator = ";"
        self.white_list = []
        self.demo_white_list = [
            "Parkinson",
            "EL",
            "Ambu",
            "NAZ",
            "RTW",
            "NAz",
            "FU",
            "VU",
            "Schwäche",
            "Pat.",
            "Pat",
            "AZ",
            "SZ",
            "REGA",
            "Rega",
            "NWS",
            "CA",
            "Hirn",
            "USB",
            "RQW",
            "PVK",
            "Schulter",
            "Schwindel",
            "Kopf",
            "NFS",
            "Ileus",
            "SBB",
            "UPK",
            "O2",
            "Nierenkolik",
            "Abszess",
            "Clara NFS",
            "CRB",
            "BD",
            "HWI",
        ]
        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()

    def show_settings(self):
        self.input_type = st.radio(
            "Format deines Input für die Anonymisierung", options=self.formats
        )
        if self.formats.index(self.input_type) == 0:

            with open(DEMO_FILENAME, "r", encoding="utf-8") as f:
                text = f.read()
            self.text = st.text_area(
                label="Text eingeben",
                value=text,
                height=300,
            )
            self.white_list = self.demo_white_list
        else:
            file = st.file_uploader("Datei hochladen")
            if file:
                st.success("Datei erfolgreich hochgeladen!")

        file = st.file_uploader(
            "Whitelist hochladen",
            help="Wörter die nicht anonymisiert werden sollen. Einfache Textdatei mit einem Wort pro Zeile",
        )
        if file:
            st.success("Whitelist erfolgreich hochgeladen!")
        self.white_list = st.multiselect(
            label="Wörter die nicht anonymisiert werden sollen",
            options=self.white_list,
            default=self.white_list,
        )

    def run(self):
        """
        Runs the anonymization process.

        If the current workstation is not a developer workstation, displays a warning message.
        Otherwise, if the "Starten" button is clicked, initializes the anonymization engine and performs the anonymization process.

        Returns:
            None
        """
        if get_hostname() not in DEV_WORKSTATIONS:
            st.warning(
                """"Wir bitten um Entschuldigung. Diese Funktion ist nur auf den Entwickler-Workstations verfügbar. 
Der Flair recognizer nimmt ca. 2GB Festlplatten Speicher in Anspruch, was die Kapazität auf der aktuellen 
Cloud-Plattform übersteigt."""
            )
        elif st.button("Starten", disabled=(get_hostname() not in DEV_WORKSTATIONS)):
            with st.spinner("Anonymisierung wird initialisiert..."):
                engine = AnonymizerEngine()
                configuration = {
                    "nlp_engine_name": "spacy",
                    "models": [
                        {"lang_code": "de", "model_name": "de_core_news_lg"},
                        {"lang_code": "en", "model_name": "en_core_web_lg"},
                    ],
                }
                flair_recognizer_de = FlairRecognizer(supported_language="de")
                # flair_recognizer_en = FlairRecognizer(supported_language="en")
                # This would download a very large (+2GB) model on the first run

                registry = RecognizerRegistry()
                registry.load_predefined_recognizers()
                phone_recognizer_ch = predefined_recognizers.PhoneRecognizer(
                    supported_language="de",
                    supported_regions=("DE", "CH"),
                )
                birthday_recognizer_ch = predefined_recognizers.DateRecognizer(
                    context=["birthday"], supported_language="de"
                )
                # registry.add_recognizer(flair_recognizer_en)
                registry.add_recognizer(flair_recognizer_de)
                registry.add_recognizer(phone_recognizer_ch)
                registry.add_recognizer(birthday_recognizer_ch)

                provider = NlpEngineProvider(nlp_configuration=configuration)
                nlp_engine_with_german = provider.create_engine()
                analyzer = AnalyzerEngine(
                    nlp_engine=nlp_engine_with_german,
                    registry=registry,
                    # supported_languages=["de", "en"],
                    supported_languages=["de"],
                )

            with st.spinner("Anonymisierung ist gestartet..."):
                cols = st.columns([8, 1, 8])
                results = analyzer.analyze(
                    self.text,
                    language="de",
                    return_decision_process=True,
                    allow_list=self.white_list,
                )
                self.text_result = engine.anonymize(
                    text=self.text, analyzer_results=results
                ).text
            if self.text_result:
                with cols[0]:
                    st.write("**Input**")
                    st.markdown(self.text)
                with cols[2]:
                    st.write("**Output**")
                    st.markdown(self.text_result)
                    st.download_button(
                        label="Download",
                        data=self.text_result,
                        file_name="anonymisiert.txt",
                        mime="text/plain",
                    )
