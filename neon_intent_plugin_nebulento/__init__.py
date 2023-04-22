from nebulento import IntentContainer, MatchStrategy
from ovos_plugin_manager.intents import IntentExtractor, IntentPriority, IntentDeterminationStrategy


class NebulentoExtractor(IntentExtractor):
    def __init__(self, config=None,
                 strategy=IntentDeterminationStrategy.SEGMENT_REMAINDER,
                 priority=IntentPriority.MEDIUM,
                 segmenter=None):
        super().__init__(config, strategy=strategy,
                         priority=priority, segmenter=segmenter)
        fuzzy_strategy = self.config.get("fuzzy_strategy", "ratio")
        if fuzzy_strategy == "ratio":
            fuzzy_strategy = MatchStrategy.RATIO
        elif fuzzy_strategy == "token_set_ratio":
            fuzzy_strategy = MatchStrategy.TOKEN_SET_RATIO
        elif fuzzy_strategy == "token_sort_ratio":
            fuzzy_strategy = MatchStrategy.TOKEN_SORT_RATIO
        elif fuzzy_strategy == "partial_token_set_ratio":
            fuzzy_strategy = MatchStrategy.PARTIAL_TOKEN_SET_RATIO
        elif fuzzy_strategy == "partial_token_sort_ratio":
            fuzzy_strategy = MatchStrategy.PARTIAL_TOKEN_SORT_RATIO
        else:
            fuzzy_strategy = MatchStrategy.SIMPLE_RATIO
        self.fuzzy_strategy = fuzzy_strategy
        self.engines = {}  # lang: IntentContainer

    def _get_engine(self, lang=None):
        lang = lang or self.lang
        if lang not in self.engines:
            self.engines[lang] = IntentContainer(fuzzy_strategy=self.fuzzy_strategy)
        return self.engines[lang]

    def detach_intent(self, intent_name):
        for intent in self.registered_intents:
            if intent.name == intent_name and intent.lang in self.engines:
                if intent_name in self.engines[intent.lang].registered_intents:
                    self.engines[intent.lang].registered_intents.remove(intent_name)
        super().detach_intent(intent_name)

    def register_entity(self, entity_name, samples=None, lang=None):
        lang = lang or self.lang
        engine = self._get_engine(lang)
        super().register_entity(entity_name, samples)
        engine.add_entity(entity_name, samples)

    def register_intent(self, intent_name, samples=None, lang=None):
        lang = lang or self.lang
        engine = self._get_engine(lang)
        super().register_intent(intent_name, samples)
        engine.add_intent(intent_name, samples)

    # matching
    def calc_intent(self, utterance, min_conf=0.6, lang=None, session=None):
        lang = lang or self.lang
        engine = self._get_engine(lang)
        intent = engine.calc_intent(utterance)
        intent["intent_engine"] = "nebulento"
        intent["intent_type"] = intent.pop("name")
        if intent["conf"] < min_conf:
            intent = {"conf": 0,
                      "intent_type": "unknown",
                      "intent_engine": "nebulento",
                      'entities': {},
                      "match_strategy": self.fuzzy_strategy,
                      "utterance_remainder": utterance,
                      'utterance_consumed': ""}
        else:
            # HACK - nebulento returns a list, api expects single entry
            intent["entities"] = {k: v[0] for k, v in intent["entities"].items() if v}
            # HACK - normalize some stuff
            intent["utterance_remainder"] = intent["utterance_remainder"].lstrip(",.;:!?\"' ").rstrip(",.;:!?\"' ")
            intent["utterance_consumed"] = intent["utterance_consumed"].lstrip(",.;:!?\"' ").rstrip(",.;:!?\"' ")
        return intent