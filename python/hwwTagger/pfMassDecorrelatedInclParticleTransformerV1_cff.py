import FWCore.ParameterSet.Config as cms

from PhysicsTools.PFNano.pfCustomDeepBoostedJetTagInfos_cfi import pfCustomDeepBoostedJetTagInfos
from RecoBTag.ONNXRuntime.boostedJetONNXJetTagsProducer_cfi import boostedJetONNXJetTagsProducer
from PhysicsTools.PFNano.hwwTagger.pfMassDecorrelatedInclParticleTransformerV1DiscriminatorsJetTags_cfi import pfMassDecorrelatedInclParticleTransformerV1DiscriminatorsJetTags

pfMassDecorrelatedInclParticleTransformerV1TagInfos = pfCustomDeepBoostedJetTagInfos.clone(
    use_puppiP4 = False
)

pfMassDecorrelatedInclParticleTransformerV1JetTags = boostedJetONNXJetTagsProducer.clone(
    src = 'pfMassDecorrelatedInclParticleTransformerV1TagInfos',
    preprocess_json = 'PhysicsTools/PFNano/data/InclParticleTransformer-MD/ak8/V01/preprocess_corr.json',
    model_path = 'PhysicsTools/PFNano/data/InclParticleTransformer-MD/ak8/V01/model.onnx',
    flav_names = [
        "probHWqqWqq0c", "probHWqqWqq1c", "probHWqqWqq2c", "probHWqqWq0c", "probHWqqWq1c", "probHWqqWq2c", # feats 0-5
        "probHWqqWev0c", "probHWqqWev1c", "probHWqqWmv0c", "probHWqqWmv1c", # feats 6-9
        "probHWqqWtauev0c", "probHWqqWtauev1c", "probHWqqWtaumv0c", "probHWqqWtaumv1c", "probHWqqWtauhv0c", "probHWqqWtauhv1c", # feats 10-15
        "probHbb", "probHcc", "probHss", "probHqq", "probHtauhtaue", "probHtauhtaum", "probHtauhtauh", # feats 16-22
        "probQCDbb", "probQCDcc", "probQCDb", "probQCDc", "probQCDothers", # feats 23-27
        "probTopbWqq0c", "probTopbWqq1c", "probTopbWq0c", "probTopbWq1c", "probTopbWev", "probTopbWmv", "probTopbWtauhv", "probTopbWtauev", "probTopbWtaumv", # feats 28-36
        "mass", # feats 37
    ] + ['hidNeuron%s' % str(idx).zfill(3) for idx in range(128)], # feats 38-165
    debugMode = False,
)

# declare all the discriminators
# probs
_pfMassDecorrelatedInclParticleTransformerV1JetTagsProbs = ['pfMassDecorrelatedInclParticleTransformerV1JetTags:' + flav_name
                                 for flav_name in pfMassDecorrelatedInclParticleTransformerV1JetTags.flav_names]
# meta-taggers
_pfMassDecorrelatedInclParticleTransformerV1JetTagsMetaDiscrs = ['pfMassDecorrelatedInclParticleTransformerV1DiscriminatorsJetTags:' + disc.name.value()
                                      for disc in pfMassDecorrelatedInclParticleTransformerV1DiscriminatorsJetTags.discriminators]

_pfMassDecorrelatedInclParticleTransformerV1JetTagsAll = _pfMassDecorrelatedInclParticleTransformerV1JetTagsProbs + _pfMassDecorrelatedInclParticleTransformerV1JetTagsMetaDiscrs
