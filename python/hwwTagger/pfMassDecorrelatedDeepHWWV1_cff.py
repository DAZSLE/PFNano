import FWCore.ParameterSet.Config as cms

from RecoBTag.FeatureTools.pfDeepBoostedJetTagInfos_cfi import pfDeepBoostedJetTagInfos
from RecoBTag.ONNXRuntime.boostedJetONNXJetTagsProducer_cfi import boostedJetONNXJetTagsProducer
from PhysicsTools.PFNano.hwwTagger.pfMassDecorrelatedDeepHWWV1DiscriminatorsJetTags_cfi import pfMassDecorrelatedDeepHWWV1DiscriminatorsJetTags

pfMassDecorrelatedDeepHWWV1TagInfos = pfDeepBoostedJetTagInfos.clone(
    use_puppiP4 = False
)

pfMassDecorrelatedDeepHWWV1JetTags = boostedJetONNXJetTagsProducer.clone(
    src = 'pfMassDecorrelatedDeepHWWV1TagInfos',
    preprocess_json = 'PhysicsTools/PFNano/data/DeepHWW-MD/ak8/V01/preprocess_corr.json',
    model_path = 'PhysicsTools/PFNano/data/DeepHWW-MD/ak8/V01/model.onnx',
    flav_names = ["probHww4q", "probHww3q", "probHwwevqq", "probHwwmvqq", "probHwwleptauevqq", "probHwwleptaumvqq", "probHwwhadtauvqq",
                  "probQCDbb", "probQCDcc", "probQCDb", "probQCDc", "probQCDothers"],
    debugMode = False,
)

# declare all the discriminators
# probs
_pfMassDecorrelatedDeepHWWV1JetTagsProbs = ['pfMassDecorrelatedDeepHWWV1JetTags:' + flav_name
                                 for flav_name in pfMassDecorrelatedDeepHWWV1JetTags.flav_names]
# meta-taggers
_pfMassDecorrelatedDeepHWWV1JetTagsMetaDiscrs = ['pfMassDecorrelatedDeepHWWV1DiscriminatorsJetTags:' + disc.name.value()
                                      for disc in pfMassDecorrelatedDeepHWWV1DiscriminatorsJetTags.discriminators]

_pfMassDecorrelatedDeepHWWV1JetTagsAll = _pfMassDecorrelatedDeepHWWV1JetTagsProbs + _pfMassDecorrelatedDeepHWWV1JetTagsMetaDiscrs
