import FWCore.ParameterSet.Config as cms

pfMassDecorrelatedDeepHWWV1DiscriminatorsJetTags = cms.EDProducer(
   'BTagProbabilityToDiscriminator',
   discriminators = cms.VPSet(
      cms.PSet(
         name = cms.string('probHww4qvsQCD'),
         numerator = cms.VInputTag(
            cms.InputTag('pfMassDecorrelatedDeepHWWV1JetTags', 'probHww4q'),
            ),
         denominator = cms.VInputTag(
            cms.InputTag('pfMassDecorrelatedDeepHWWV1JetTags', 'probHww4q'),
            cms.InputTag('pfMassDecorrelatedDeepHWWV1JetTags', 'probQCDbb'),
            cms.InputTag('pfMassDecorrelatedDeepHWWV1JetTags', 'probQCDcc'),
            cms.InputTag('pfMassDecorrelatedDeepHWWV1JetTags', 'probQCDb'),
            cms.InputTag('pfMassDecorrelatedDeepHWWV1JetTags', 'probQCDc'),
            cms.InputTag('pfMassDecorrelatedDeepHWWV1JetTags', 'probQCDothers'),
            ),
         ),
      cms.PSet(
         name = cms.string('probHww4q3qvsQCD'),
         numerator = cms.VInputTag(
            cms.InputTag('pfMassDecorrelatedDeepHWWV1JetTags', 'probHww4q'),
            cms.InputTag('pfMassDecorrelatedDeepHWWV1JetTags', 'probHww3q'),
            ),
         denominator = cms.VInputTag(
            cms.InputTag('pfMassDecorrelatedDeepHWWV1JetTags', 'probHww4q'),
            cms.InputTag('pfMassDecorrelatedDeepHWWV1JetTags', 'probHww3q'),
            cms.InputTag('pfMassDecorrelatedDeepHWWV1JetTags', 'probQCDbb'),
            cms.InputTag('pfMassDecorrelatedDeepHWWV1JetTags', 'probQCDcc'),
            cms.InputTag('pfMassDecorrelatedDeepHWWV1JetTags', 'probQCDb'),
            cms.InputTag('pfMassDecorrelatedDeepHWWV1JetTags', 'probQCDc'),
            cms.InputTag('pfMassDecorrelatedDeepHWWV1JetTags', 'probQCDothers'),
            ),
         ),
      )
   )
