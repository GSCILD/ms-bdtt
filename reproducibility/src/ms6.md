# 6. Conclusion

## 6.1 Summary

This paper presented MS-BDTT, a three-stage framework for cross-domain fault diagnosis in marine power systems that addresses the scarcity of labelled data under continuous operating-condition drift. The framework integrates three innovations: a parameterised rotordynamic simulator with demand-guided sampling that generates physically consistent synthetic fault signatures over a continuous operating envelope; a Bayesian particle-filter calibrator that aligns simulation outputs with reference sensor data using unlabelled normal-condition measurements only and reduces the simulator-to-measurement gap by 65.7 % in MMD; and an attention-weighted adversarial transfer network that selectively exploits bridge data while suppressing the 37 % of bridge samples with the lowest learned relevance to mitigate negative transfer. Validation on four public rotating-machinery datasets, a high-fidelity marine propulsion simulator and the synthetic SPFD shows that MS-BDTT attains a five-scenario macro-average accuracy of 83.9 % (range 76.0–96.5 %), exceeding the strongest baseline COSDA by 3.6 percentage points, and 76.0 ± 3.5 % sample-weighted overall accuracy in the most challenging unlabelled-target scenario, in which it surpasses all baselines by at least 6.8 percentage points. A ten-seed paired replication confirms these margins within their run-to-run dispersion (+3.58 ± 0.58 pp, 95 % CI [3.16, 4.00] on the macro-average; +6.83 ± 1.25 pp, 95 % CI [5.94, 7.72] on S5), and the measured retention and budget sweeps locate the suppression and sampling operating points used in Sections 3.5 and 5.7 instead of assuming them. The ablation study is consistent with each component contributing non-redundantly: the continuous bridge accounts for 6.2 percentage points, Bayesian calibration for 5.9, the physical consistency loss for 4.0, demand-guided sampling for 3.4, the attention mechanism for 2.6 and the adversarial loss for 1.8 (three-scenario macro-averages; exploratory). The grid-level results remain labelled exploratory, and all results are regenerated from one auditable source with the full reproducibility package on Zenodo.

## 6.2 Key findings

Three findings emerge as particularly significant for the marine power diagnostics community.

First, continuous interpolation, not the transfer algorithm, is the dominant factor in this study. Replacing a single source–target jump by a chain of adjacent bridge domains removes 43.8 of the 86.6 percentage points of total domain-gap reduction, and removing the bridge costs 6.2 percentage points of accuracy, more than any other component. We interpret this strictly as empirical evidence for the benefit of a physically meaningful interpolation path in these experiments; the divergence decomposition of Eq. (14) motivates the construction but does not itself guarantee a reduction of population divergence (Section 3.7).

Second, Bayesian calibration makes sparse unlabelled data genuinely useful for structural corrections. Bayesian calibration contributes 21.9 percentage points of the 65.7 % cumulative domain-gap reduction (the remaining 43.8 percentage points come from the continuous bridge) through posterior inference on 120 unlabelled normal-condition samples, which suggests that even very limited measurements can substantially reduce the measured simulator-to-measurement discrepancy in MMD. The calibration state comprises the structural corrections [k, c] only; severity is never updated from healthy data, and the identifiability of the calibrated state is characterised, not assumed, by the diagnostics of Appendix E.2. The result is relevant beyond marine engineering, wherever a high-fidelity simulator exists but calibration data are scarce.

Third, attention weighting measurably reduced the risk of negative transfer in our experiments. Because four heterogeneous source datasets are merged in S5, uniform aggregation would invite negative transfer; suppressing the 37 % of bridge samples with the lowest learned relevance improved S5 accuracy by 3.9 percentage points over no suppression (76.0 % versus 72.1 %), and the measured retention sweep places the maximum of the accuracy curve and the minimum of the domain gap at the same 63 % operating point (83.9 % against 81.2 % without suppression and 77.4 % at 20 % retention). The scenario-level margin over the baselines remains 6.8 percentage points. We describe this as reduced negative-transfer risk under the tested conditions rather than as a guarantee of safe aggregation in general.

## 6.3 Limitations

Several limitations deserve acknowledgement. The mechanistic simulator requires accurate geometric and material parameters, which may not be available for legacy vessels with incomplete maintenance records. The particle filter assumes Gaussian process noise, an assumption that is violated by the abrupt parameter changes caused by catastrophic failures such as a sudden bearing seizure. The effectiveness of the attention mechanism depends on the quality of the bridge samples: if the simulator produces systematically biased outputs, the attention weights may learn to compensate in undesirable ways rather than reject the biased samples. The identifiability of the Bayesian calibration is characterised by the recovery, predictive-check and coverage diagnostics of Appendix E.2 rather than established in general; the prior-mismatch results of Appendix E.1 are robustness evidence only. The severity mapping between laboratory defect sizes and marine wear stages (Section 4.2.5) is a modelling assumption. The supervision for the misalignment and cavitation classes in S5 derives from simulator bridge prototypes and is labelled as such; conclusions about those two classes are correspondingly weaker than conclusions about classes grounded in laboratory measurements.

The SPFD dataset used in this study is synthetic rather than measured on an operating vessel. Although MarineSim incorporates physics-based models validated against published measurements, synthetic data cannot capture the full complexity of shipboard conditions, including irregular sea states, multi-source noise interference and long-term equipment degradation. Validating the framework on measured data from an operational vessel remains the most important next step, and collaboration with shipping companies is being pursued for that purpose. All marine claims in this paper are bounded by this synthetic validation.

The current formulation addresses single-fault scenarios primarily. Composite faults involving multiple simultaneous degradation modes remain challenging, at 61.2 % overall accuracy on SPFD, because the lumped-parameter rotordynamic model does not capture nonlinear fault-coupling effects such as the interaction between shaft misalignment and bearing wear, and because L_phy encodes single-fault spectral constraints only (Section 3.8). Extending the framework to multi-fault diagnosis will require either richer physics-based simulation or hybrid physics–data-driven modelling.

## 6.4 Future work

Four directions are identified for future investigation. First, enhanced model fidelity through multi-body dynamics and physics-informed neural networks could capture complex fault interactions and reduce dependence on precise geometric parameters. Second, meta-learning-based initialisation could enable rapid adaptation to new vessel types with minimal calibration data, reducing the current requirement of about 120 unlabelled samples. Third, active learning strategies could identify the most informative operating conditions for bridge generation and further improve data efficiency. Fourth, integration with exergy analysis has been suggested as a route to energy-loss-based fault localisation; we note explicitly that the present study reports no energy or exergy measurements and makes no quantified energy-related claim, so this direction remains unquantified motivation rather than a result.

## 6.5 Practical and regulatory implications

MS-BDTT offers a practical pathway for deploying intelligent fault diagnosis on vessels where labelled data are inherently scarce. By exploiting existing mechanistic models and requiring only unlabelled normal-condition data for calibration, it reduces the data-collection burden that has historically limited the adoption of deep learning in maritime applications. The 1.2 ms inference latency supports real-time monitoring on standard marine edge controllers, and the 85 min one-time training cost is amortised over a vessel's decades-long operational lifetime; we reiterate that inference latency alone does not establish operational diagnostic reliability, which the synthetic evidence of this paper cannot. With regard to classification-society guidelines for smart-ship certification, data-driven systems are expected to provide auditable diagnostic outputs with uncertainty quantification, explainable decision processes and traceable model updates. The Bayesian calibration stage supplies posterior uncertainty over the calibration parameters, and the attention weights provide a sample-level explanation of which simulated operating conditions supported a decision, so the framework addresses these requirements at least partially; a systematic conformity assessment against specific class rules is nevertheless left for future work, together with validation on measured ship data.

# Code and data availability

The complete reproducibility package is deposited in a public, DOI-assigning software archive (⟦FILL-ARCHIVE⟧; ⟦FILL-ARCHIVE-ID⟧) and mirrored in the version-controlled repository at https://github.com/GSCILD/ms-bdtt, whose tagged release notes record the immutable commit hash of the snapshot reviewed for this submission. The archive is one of the DOI-assigning repositories accepted for this purpose, and the deposited snapshot is additionally archived in the Software Heritage long-term source-code archive, so that the reviewed version remains citable independently of the availability of the hosting platform. The deposit is uploaded as a single archive, ms-bdtt-reproducibility-package.zip, and is accompanied by a SHA256SUMS.txt checksum file covering every deposited file. Its data/ directory contains the source workbook of the supplemental experiments together with the confirmatory-analysis kit that regenerates each result file from that workbook, so that the confirmatory numbers of Tables 9, 8b, D.2, D.3, E.2 and C.2 can be recomputed without access to the training hardware; its src/ directory contains the markdown sources of this manuscript and of the point-by-point response, and its code/build/ directory the scripts that regenerate both documents. The archive contains: (i) the source code of all three stages and of all ten baselines, including configuration files with the exact hyperparameters of Appendix D; (ii) the split manifests of Section 4.4 as CSV files with SHA-256 checksums, including the transformed S2 records with their parent-record partition inheritance; (iii) the exact random seeds and per-run command lines; (iv) the trained model weights; (v) the run-level predictions and per-run metrics underlying every mean, standard deviation, confidence interval and test statistic; (vi) the raw per-scenario and per-stage MMD values of Appendix C.4; (vii) one regeneration script per table and figure, which reproduces every numerical claim in this paper from the deposited artefacts alone; and (viii) the scripted confirmatory analyses themselves — the ten-seed paired replication of Section 5.6, the S4 open-set evaluation with its leakage-safe rejection threshold (Section 4.2.4), the retention and budget sweeps of Appendix D.2, the identifiability diagnostics of Appendix E.2, the degradation-boundary labelling of Section 4.2.3 and the manifest-generation and leakage-check toolkit of Section 4.4 — together with the measured outputs of those analyses and the source workbook from which they are regenerated, so that every number requested during review is produced by a deposited script rather than by hand. MarineSim inputs and the SPFD generation scripts are included in the same archive. The authors confirm that the archive is publicly accessible and that the DOI resolves.

# Declarations

## Author contributions

Dong Liu: conceptualisation, methodology, software, writing of the original draft. Jie Liu: supervision, writing, review and editing, project administration. Both authors contributed to the experimental design and to the data analysis, and both approved the final manuscript.

## Conflict of interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

## Data availability

All data used in this study are either publicly available from their providers (CWRU [36], XJTU-SY [37], Paderborn [38], SEU [39]) or generated by the MarineSim and SPFD scripts included in the Zenodo archive described under Code and data availability. The dataset provenance tables of Appendix F document every file identifier, channel, sampling rate, operating condition, label rule, exclusion and preprocessing step.

## Acknowledgements

The authors thank the anonymous reviewers for their constructive comments, which substantially improved the clarity and the rigour of this paper.

## Funding

The authors declare that no financial grants or other forms of financial support were received from any funding agency, commercial enterprise, or non-profit organization for the research, authorship, and/or publication of this article.

# Nomenclature

Roman symbols

M, C, G, K: mass, damping, gyroscopic and stiffness matrices

q: generalised displacement vector

F(t): external excitation force

x_sim, x_meas: simulated and measured vibration signals

n_sensor, n_ambient: sensor and ambient noise terms

H_s(f): sensor frequency response function

d_MMD: maximum mean discrepancy

m(θ_o): demand map over the operating envelope

κ: classification accuracy used in the fault-sensitivity gradient

s: fault severity (Stage-1 injection parameter; not a calibration state)

k, c: stiffness and damping correction factors (the calibration state [k, c]ᵀ)

Φ: band-limited spectral feature vector

h(x): classifier; H: hypothesis class

z_q, z_b: query and bridge feature vectors

d_h: hidden dimension of the attention network

N: number of particles; N_k: samples allocated to node k

K: number of bridge interpolation nodes

Ê_Θ(f_c): attention-weighted band energy at characteristic frequency f_c

E_c^{ref}: analytically predicted reference energy of band c

τ_rej: unknown-rejection threshold (S4 open-set track)

Greek symbols

Ω: rotational speed

θ_o: operating-parameter vector (speed, mean effective pressure, alignment)

θ_t: digital-twin calibration state [k, c]ᵀ

ε_t, v_t: process and observation noise

σ: likelihood scale of the particle filter

α: demand-map weighting coefficient

λ: weight of the adversarial loss; λ*: ideal joint risk

μ: weight of the physical consistency loss

τ: temperature of the attention distribution

ε_t(h): target risk of hypothesis h

δ: confidence parameter

Subscripts and superscripts

S, T: source and target

b: bridge

sim, meas: simulated and measured

o: operating point
