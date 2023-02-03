# Introduction

This model is the first practice of training an all-inclusive tagger trained in the mass decorrelation scheme, with the goal of presenting a **large pre-trained model for large-scale classification for HEP**. The model uses the Particle Transformer [[paper](https://arxiv.org/abs/2202.03772)][[github](https://github.com/jet-universe/particle_transformer)] architecture as the backbone.

The output of the model includes 37 raw scores for jet classification, one value of regressed mass to estimate the mass of the gen-level resonance which originate the jet, and 128 hidden neuron scores.

1. The 37 raw scores are named by `probXXX`, which include:

    | Jet types | Scores |
    | ------- | ------ |
    | H→WW→qqqq | `probHWqqWqq0c`, `probHWqqWqq1c`, `probHWqqWqq2c`, `probHWqqWq0c`, `probHWqqWq1c`, `probHWqqWq2c` |
    | H→WW→e/μνqq | `probHWqqWev0c`, `probHWqqWev1c`, `probHWqqWmv0c`, `probHWqqWmv1c` |
    | H→WW→τνqq | `probHWqqWtauev0c`, `probHWqqWtauev1c`, `probHWqqWtaumv0c`, `probHWqqWtaumv1c`, `probHWqqWtauhv0c`, `probHWqqWtauhv1c` |
    | H→bb/cc/ss/qq/ττ | `probHbb`, `probHcc`, `probHss`, `probHqq`, `probHtauhtaue`, `probHtauhtaum`, `probHtauhtauh` |
    | QCD | `probQCDbb`, `probQCDcc`, `probQCDb`, `probQCDc`, `probQCDothers` |
    | t→bW→bqq | `probTopbWqq0c`, `probTopbWqq1c`, `probTopbWq0c`, `probTopbWq1c` |
    | t→bW→bℓν | `probTopbWev`, `probTopbWmv`, `probTopbWtauhv`, `probTopbWtauev`, `probTopbWtaumv` |

2. The regressed mass value takes the name `mass`.

3. The 128 neuron scores in the hidden layer before the classification/regression head are also accessible. and a, with the name `hidNeuronsXXX`, where `XXX` goes from `000` to `127`. The purpose of exposing hidden neuron scores is to practice the "pre-training and fine-tuning" scheme in deep learning and facilitate the downstream tasks (analyses) to use these scores for customized fine-tuning jobs.


# Usage

Analyses can use the scores in the conventional discriminant approach or a more advanced fine-tuning approach.

## Discriminants

Depending on the signal type and the dominant backgrounds, one can choose to define, e.g.,

 - `HbbvsQCD := probHbb / (probHbb + Σ prob(QCD))`, for H→bb vs. QCD discrimination, where `Σ prob(QCD)` is the sum of all probability scores in the categories shown above;
 - `HWW4qvsQCD := (probHWqqWqq0c + probHWqqWqq1c + probHWqqWqq2c) / (probHWqqWqq0c + probHWqqWqq1c + probHWqqWqq2c + Σ prob(QCD))`, for H→WW→4q vs. QCD discrimination;
 - `HWWlvqqvsTopblv := (Σ prob(H→WW→e/μνqq) + Σ prob(H→WW→τνqq)) / (Σ prob(H→WW→e/μνqq) + Σ prob(H→WW→τνqq) + Σ prob(t→bW→bqq))`, for H→WW→ℓνqq vs. t→bW→bℓν discrimination (when tt̅ process with 1 lepton is the dominant background);
 - `HWWlvqqvsQCDTop := (Σ prob(H→WW→e/μνqq) + Σ prob(H→WW→τνqq)) / (Σ prob(H→WW→e/μνqq) + Σ prob(H→WW→τνqq) + α * Σ prob(QCD) + β * (Σ prob(t→bW→bqq) + Σ prob(t→bW→bℓν)))`, for H→WW→ℓνqq vs. both QCD and top discrimination (when both QCD and tt̅ are backgrounds). It is possible to tune the parameters α and β, depending on the relative proportion of QCD and tt̅ as background events in a specific analysis.

## Fine-tuning

Fine-tuning means taking a model that has been pre-trained on a particular task and further training it on a second similar task. A larger pre-trained model should be more adaptive to the new tasks. Usually, when fine-tuning a large model, the last layer will be replaced by a new one for training, while the rest of the network can keep unchanged or be allowed to update slowly. Here, we note that attempting to fine-tune the model in the first approach is equivalent to building a new and simple network upon the hidden neurons of the large model we dedicatedly expose. Hence, we have the following scheme for fine-tuning as an example.

 - **Fine-tuning on the class discriminants**: use the hidden neuron scores as input, and build a simple NN or a BDT model to train on customized classification tasks, e.g. identification of a type of jets not included in the above categories.
 - **Fine-tuning on the regressed mass**: use the hidden neurons scores as input, along with some event-level variables, e.g., the MET features, and build a simple NN to train with a regression target again on the gen-level resonance mass. This will improve the regressed mass resolution as we introduce new input features.
 - In fact, any attempt to use these hidden neuron scores of a jet to further train an ML model is essentially a fine-tuning of the original model. This opens up a variety of new possibilities for future analyses.


# Appendix

## Notes on the training samples

Dedicated training samples are produced for the purpose of mass decorrelation.

 - **H→WW→qqqq/ℓνqq**: jets are produced from bulk graviton to HH to four Ws samples using MadGraph, where graviton mass and Higgs mass are allowed to vary. The graviton mass is set in 600-6000 GeV range and Higgs mass in 15-250 GeV. The cascade decay of H→WW→qqqq/ℓνqq is treated by JHUGen, with the W mass configured to maintain the m_W/m_H ratio constant.
 - **H→bb/cc/ss/qq/ττ**: jets are produced from bulk graviton to HH to four quarks sample using MadGraph, where graviton mass and Higgs mass are allowed to vary, same as above. Note that tis sample configuration is the same as the one used for official ParticleNet-MD training.
 - **Top**: jets are produced from bulk graviton to tt̅ to top final states using MadGraph. The graviton mass is allowed to vary from 600-6000 GeV and t(t̅) mass from 15-250 GeV range. The W boson mass is configured to maintain the m_W/m_t ratio constant, with a minimum threshold of 80 GeV. The width of the W is set equal to the W mass so that the truth W mass is allowed to further vary in a wide range.
 - **QCD**: jets are collected from the HT-binned QCD multijet MadGraph sample.

## Memo
This version corresponds to the model on PKU zeus/farm221 `/home/olympus/licq/hww/incl-train/weaver-core/weaver/model/ak8_MD_vminclv2ParT_manual_fixwrap`.

## Update note:

 - V1: First version.
