from nebulento import IntentContainer, MatchStrategy
from ovos_plugin_manager.templates.intents import IntentExtractor


class NebulentoExtractor(IntentExtractor):
    keyword_based = False

    def __init__(self, fuzzy_strategy=MatchStrategy.SIMPLE_RATIO, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = IntentContainer(fuzzy_strategy=fuzzy_strategy)

    def detach_intent(self, intent_name):
        super().detach_intent(intent_name)
        if intent_name in self.engine.registered_intents:
            self.engine.registered_intents.remove(intent_name)

    def register_entity(self, entity_name, samples=None):
        super().register_entity(entity_name, samples)
        self.engine.add_entity(entity_name, samples)

    def register_intent(self, intent_name, samples=None):
        super().register_intent(intent_name, samples)
        self.engine.add_intent(intent_name, samples)

    # matching
    def calc_intent(self, utterance, min_conf=0.6):
        intent = self.engine.calc_intent(utterance)
        intent["intent_engine"] = "nebulento"
        intent["intent_type"] = intent.pop("name")
        if intent["conf"] < min_conf:
            intent = {"conf": 0,
                      "intent_type": "unknown",
                      "intent_engine": "nebulento",
                      'entities': {},
                      "match_strategy": self.strategy,
                      "utterance_remainder": utterance,
                      'utterance_consumed': ""}
        else:
            # HACK - nebulento returns a list, api expects single entry
            intent["entities"] = {k: v[0] for k, v in intent["entities"].items() if v}
            # HACK - normalize some stuff
            intent["utterance_remainder"] = intent["utterance_remainder"].lstrip(",.;:!?\"' ").rstrip(",.;:!?\"' ")
            intent["utterance_consumed"] = intent["utterance_consumed"].lstrip(",.;:!?\"' ").rstrip(",.;:!?\"' ")
        return intent

    def intent_scores(self, utterance):
        utterance = utterance.strip().lower()
        intents = []
        bucket = self.calc_intents(utterance)
        for utt in bucket:
            intent = bucket[utt]
            if not intent:
                continue
            intents.append(intent)
        return intents

    def calc_intents(self, utterance, min_conf=0.6):
        bucket = {}
        for ut in self.segmenter.segment(utterance):
            intent = self.calc_intent(ut)
            bucket[ut] = intent
        return bucket

    def calc_intents_list(self, utterance):
        utterance = utterance.strip().lower()
        bucket = {}
        for ut in self.segmenter.segment(utterance):
            bucket[ut] = self.filter_intents(ut)
        return bucket
