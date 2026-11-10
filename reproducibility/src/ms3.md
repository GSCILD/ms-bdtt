## 3.4 Bayesian digital twin calibration

### 3.4.1 State-space formulation

The digital twin is formulated as a stochastic state-space model:

θ_t = f(θ_{t−1}) + ε_t ,  ε_t ~ N(0, Σ_θ)    (6)

Y_t = h(θ_t, x_sim(θ_t)) + v_t ,  v_t ~ N(0, Σ_y)    (7)

The calibration state θ_t = [k, c]ᵀ contains a stiffness correction factor k and a damping correction factor c. The state deliberately contains no severity component: fault severity is a property of the fault injection in the Stage-1 simulator (the parameter η or s of Appendix A), not a quantity that can be inferred from healthy-condition measurements, and the calibration data used in this study are unlabelled normal-condition readings only. The filter therefore updates the structural corrections exclusively; the severity output of the diagnostic head in Stage 3 is a classification posterior, not a filtered state. This resolves the inconsistency, flagged during review, between a three-component state and the normal-condition-only calibration protocol. The process model f(·) encodes the physical constraint that the correction factors evolve slowly relative to the sampling rate; Σ_θ is diagonal, with process-noise standard deviations of 0.01 for k and 0.02 for c. The observation model h(·) computes the spectral coherence between simulated and measured vibration in the fault characteristic frequency bands.

Prior distributions are set from engineering knowledge. Stiffness coefficients follow truncated normal distributions centred on finite element predictions with a 10 % standard deviation, reflecting manufacturing tolerances specified for balance quality classes [31]; damping ratios follow log-normal distributions whose medians are calibrated from healthy-condition baseline tests. These priors encode expert judgement while remaining sufficiently diffuse to allow posterior updating from data. Appendix E.1 shows that the framework is robust to moderate prior misspecification; robustness to prior mismatch is a necessary but not sufficient condition for identifiability, and Appendix E.2 therefore additionally reports controlled parameter-recovery, posterior-predictive-check and coverage diagnostics for the [k, c] state.

### 3.4.2 Particle filter implementation

A particle filter with N = 500 particles approximates the posterior distribution p(θ_t | y_{1:t}). The likelihood measures the spectral coherence between simulated and measured vibration in the fault characteristic frequency bands:

p( y_t | θ_t⁽ⁱ⁾ ) = exp( − ‖Φ_sim(θ_t⁽ⁱ⁾) − Φ_meas‖² / 2σ² )    (8)

where Φ denotes the band-limited spectral feature vector and σ = 0.1 is calibrated from healthy baseline data. Systematic resampling is triggered when the effective sample size (ESS) falls below N/2 = 250, which prevents particle degeneracy [32]. The choice N = 500 balances accuracy and computational cost: Section 5.5 shows that doubling to N = 1000 improves accuracy by only 0.7 percentage points while doubling the calibration time from 2.3 s to 4.6 s per step. Algorithm 1 in Appendix C gives the full procedure.

[[FIG3]]

Figure 3. Bayesian particle-filter calibration (Section 3.4). (a) Calibration loop: N = 500 particles are initialised from the prior, propagated through the process model of Eq. (6), weighted by the spectral-coherence likelihood of Eq. (8) against unlabelled normal-condition measurements from SPFD, resampled systematically when the effective sample size falls below N/2 = 250, and reduced to the posterior mean of the two-component structural correction state [k, c], which is fed back to the simulator of Stage 1; fault severity is not a component of the filtered state. (b) Cumulative simulator-to-measurement gap reduction versus iteration for the calibrated twin and for an uncalibrated bridge; the calibrated loop converges to the 65.7 % MMD reduction reported in Table 6.

## 3.5 Attention-weighted adversarial transfer

### 3.5.1 Feature extractor and attention mechanism

A one-dimensional residual convolutional neural network (1D ResCNN) with six residual blocks extracts discriminative features from the calibrated bridge samples; the channel dimensions of the blocks are [64, 128, 256, 256, 512, 512]. Each residual block consists of two convolutional layers with batch normalisation and ReLU activation, followed by a skip connection that preserves low-level temporal features; when the number of channels changes, the identity branch is replaced by a 1 × 1 convolution. Global average pooling over the time axis yields a 512-dimensional feature vector z.

Sample-level attention weights are computed by a two-layer multilayer perceptron operating on concatenated query–bridge feature pairs:

α_i = exp( ReLU( w₂ᵀ tanh( W₁ [ z_q ; z_{b,i} ] ) ) ) / Σⱼ exp( ReLU( w₂ᵀ tanh( W₁ [ z_q ; z_{b,j} ] ) ) )    (9)

where z_q ∈ R^{d_h} is the query feature obtained from the target sample, z_{b,i} ∈ R^{d_h} is the i-th bridge feature and d_h = 256, following the usual guideline of taking the hidden dimension of an attention head as approximately half of the feature dimension [33]. A temperature parameter τ = 1.0 controls the sharpness of the attention distribution: lower values produce more concentrated weighting, whereas higher values approach uniform averaging. Bridge samples whose weight falls below the relevance threshold — the 37th percentile of the learned weight distribution — are suppressed; across the five scenarios this removes 37 % of the bridge samples on average and retains 63 %.

The effect of suppression is characterised by a measured retention sweep (retention ratios {100, 80, 63, 40, 20} %, five independent runs per point, all five scenarios; Appendix D.2, Table D.2; Fig. 5). The five-scenario macro-average is 81.2 ± 0.65 % with no suppression, 82.8 ± 0.58 % at 80 %, 83.9 ± 0.52 % at the 63 % operating point, 81.5 ± 0.71 % at 40 % and 77.4 ± 0.89 % at 20 %, that is, an inverted U whose maximum coincides with the 37th-percentile relevance threshold; on S5 the same sweep gives 72.1 %, 74.3 %, 76.0 %, 72.8 % and 67.5 %. The post-suppression domain gap follows the same pattern (MMD² = 0.185, 0.154, 0.134, 0.148, 0.192), so the retained set is at once the most accurate and the most domain-aligned. The benefit of suppression is therefore attributable to the removal of low-relevance samples rather than to data reduction: 20 % retention (77.4 %) is worse than no suppression (81.2 %). The 63 % ratio remains the operating point defined by the percentile threshold of the learned attention distribution; the sweep locates it at the maximum of the measured curve, and since five ratios with five runs each are evaluated, the optimum is located rather than proved. Inverted-U behaviour in intermediate retention ratios has also been reported for related sample-selection schemes in distant-domain and cross-domain transfer [41, 42], which is consistent with the present measurement. The two-point comparison used earlier in this section, namely 63 % retained (76.0 % on S5) against 100 % retained (72.1 %), is the S5 column of the same sweep.

[[FIG4]]

Figure 4. Architecture of the transfer network (Section 3.5). Top: the 1-D ResCNN feature extractor, consisting of a 64-channel convolutional stem, six residual blocks with channel widths [64, 128, 256, 256, 512, 512] and global average pooling to the feature vector z. Middle: the sample-level attention branch, which concatenates the target query z_q with each bridge feature z_{b,i}, applies a two-layer perceptron with hidden dimension d_h = 256 (Eq. (9)) and a softmax to obtain the weight α_i, and suppresses the samples below the relevance threshold (the 37th percentile of the learned weights), 37 % of the bridge. Bottom: the gradient reversal layer (GRL) feeding the domain discriminator and the diagnostic classifier, together with the three terms of the total loss of Eq. (10).

[[FIG5]]

Figure 5. Sample-level attention and the measured evidence that suppression is beneficial (retention sweep of Appendix D.2, Table D.2). (a) Measured retention sweep: five-scenario macro-average accuracy (solid circles) and S5 accuracy (dashed squares) against the retained fraction of the bridge, with error bars giving the standard deviation over five runs per point; the vertical dotted line marks the 37th-percentile relevance threshold at which 63 % of the bridge is retained, and the curve is an inverted U whose maximum coincides with that operating point (83.9 % macro-average against 81.2 % without suppression and 77.4 % at 20 % retention). (b) Post-suppression domain gap, MMD² against the retained fraction, minimised at the same ratio (0.134 at 63 % against 0.185 without suppression and 0.192 at 20 % retention). (c) Ablation of the attention module (Table 7): removing it costs 2.6 pp on the three-scenario average (S1/S3/S5: 84.9 % → 82.3 %) and 3.9 pp on S5 (76.0 % → 72.1 %). Panels (a) and (b) are measured; the sweep evaluates five ratios with five runs per point, so the optimum is located rather than proved.

### 3.5.2 Joint optimisation objective

The total loss combines three terms:

L_total = L_diag + λ · L_adv + μ · L_phy    (10)

where L_diag is the cross-entropy classification loss on the labelled bridge samples, L_adv is the adversarial domain loss computed through gradient reversal [19, 21], and L_phy is the physical-consistency loss defined in Section 3.8. The weights λ = 0.5 and μ = 0.1 were selected by grid search on the S1 validation split (Appendix D); λ is ramped from 0 to its final value over the first 20 epochs to avoid early over-adaptation. Values of μ above 0.5 over-constrain the model to the simulated physics and reduce accuracy by 6.2 percentage points, as quantified in the ablation study of Section 5.3.

## 3.6 Unlabelled-target adaptation strategy

The unlabelled-target scenario (S5) is the most stringent test considered here: no labelled fault data from the target marine domain are available during training. The framework addresses it with a three-component strategy.

Problem definition. Given labelled source domains {M_Sᵢ} and an unlabelled target domain M_t that contains sensor measurements without fault labels, the objective is to learn a classifier h: x → y that minimises the target risk ε_t(h) without access to target labels. In this study the unlabelled target data consist of 120 normal-condition samples from SPFD, which provide sufficient spectral statistics for Bayesian calibration while respecting real-world data scarcity; these calibration samples are drawn from the calibration partition of Section 4.4 and are disjoint from the test partition.

Continuous bridge as a proxy distribution. The bridge B serves as a proxy distribution interpolating from source to target, and Bayesian calibration aligns the simulator with target-specific characteristics using unlabelled normal samples only. The attention mechanism then assigns high weights to those bridge samples whose operating conditions match the target regime, thereby constructing a target-oriented training distribution without requiring target labels. The simulator-to-measurement gap is thus closed by physics-informed interpolation rather than by direct target supervision.

Fusion mechanism. Fusion proceeds in two steps. First, the calibrated simulator generates bridge samples at the K interpolation nodes spanning the source–target operating envelope. Second, the attention network computes relevance scores between target queries and bridge samples and automatically suppresses irrelevant nodes. In this way, unlabelled-target diagnosis exploits the physically consistent synthetic data that most closely resemble the unseen target, achieving 76.0 % sample-weighted overall accuracy without any labelled marine fault data (Section 5.4 defines the metric precisely).

## 3.7 Theoretical analysis

This section states the generalisation results that motivate the design of MS-BDTT. Assumptions and proofs are given in Appendix C.

Let H be a hypothesis class of VC-dimension d_VC and let d_{HΔH} denote the H-divergence between two distributions. The classical bound of domain adaptation [34] states that for every h ∈ H,

ε_t(h) ≤ ε_S(h) + d_{HΔH}( D_S, D_T ) + λ* ,  λ* = min_{h' ∈ H} [ ε_S(h') + ε_t(h') ]    (13)

where λ* is the risk of the ideal joint hypothesis. For the continuous bridge, the H-divergence is subadditive on the symmetric difference hypothesis class, so the divergence term admits the decomposition

d_{HΔH}( D_S, D_T ) ≤ Σ_{k=0}^{K−1} d_{HΔH}( B_k, B_{k+1} ) ,  B_0 ≡ D_S ,  B_K ≡ D_T    (14)

The interpretation of Eq. (14) requires care, and we state it as follows. First, Eq. (14) is an upper-bound decomposition that holds unconditionally by subadditivity; it does not imply that the sum of adjacent divergences is smaller than the direct divergence, and hence it does not demonstrate that inserting intermediate domains reduces population divergence. Adding samples can reduce estimation error without changing population divergence. Second, what the decomposition does support is an estimation argument: under a fixed total sample budget, Proposition 2 below bounds the target risk by per-interval terms of the form d_k/√n_k, so splitting the budget across intervals can reduce the estimation contribution even when the population divergences are unchanged. Demand-guided sampling is best understood as an allocation heuristic for this estimation term. Third, whether the populated bridge reduces the population-level divergence is an empirical question; Section 5.2 reports the measured MMD reduction, and we treat the empirical tightening as observed evidence rather than as a theoretical guarantee. We deliberately refrain from claiming an exponential convergence rate for the MMD reduction, because the available evidence is empirical and does not support such a rate.

Proposition 1 (Consistency of the Bayesian calibration). Let the particle filter of Algorithm 1 evolve with N particles under Assumptions A1 (bounded likelihood) and A2 (compact parameter space). Then, for any bounded measurable test function f, the particle approximation converges to the true posterior at the usual Monte Carlo rate, that is, E| N⁻¹ Σᵢ f(θ_t⁽ⁱ⁾) − ∫ f(θ) p(θ | y_{1:t}) dθ | ≤ C / √N, where C depends on the likelihood bound and on the observation-noise variance. The result follows from standard sequential Monte Carlo convergence theory [35, 32].

Proposition 2 (Risk of attention-weighted bridge transfer). Let the bridge samples be drawn from the K bridge domains B_k with attention weights w_k ≥ 0, Σ_k w_k = 1, and let ε_b(h) = Σ_k w_k ε_{B_k}(h) be the weighted bridge risk. Then, with probability at least 1 − δ,

ε_t(h) ≤ ε_b(h) + Σ_k w_k d_{HΔH}( B_k, D_T ) + λ*_b + Ξ( d_VC, Σ_k w_k² / n_k, δ )    (15)

where λ*_b is the ideal joint risk over the bridge mixture and Ξ is a standard VC-type estimation term that depends on the effective sample size of the weighted bridge mixture. Proposition 2 shows that the attention mechanism reduces the second term by concentrating weight on the bridge domains with the smallest divergence to the target, which is the behaviour observed in Fig. 5(a). A full derivation is given in Appendix C.

Remark 1 (Sample allocation). Because the bound of Proposition 2 is additive over bridge domains, equalising the per-interval estimation terms is the budget-optimal allocation under the model. Demand-guided sampling approximates this allocation by proportional-to-demand sampling (Eq. (5)); the measured budget sweep of Appendix D.2 compares it with the uniform grid and with the theoretical d^{2/3} allocation, of which only the two former were swept experimentally (Appendix C.3).

Table 2 summarises the guarantees associated with each component of the framework and the assumptions on which they rely.

Table 2. Theoretical guarantees of the MS-BDTT components and their assumptions.

| Component | Guarantee | Key assumptions | Basis |
| --- | --- | --- | --- |
| Continuous bridge (Stage 1) | Subadditive divergence decomposition d_{HΔH}(D_S,D_T) ≤ Σ_k d_{HΔH}(B_k,B_{k+1}); no reduction of population divergence is guaranteed | H-divergence is a metric on the symmetric difference class; bridge domains are ordered along the envelope | [34], Eq. (14) |
| Demand-guided sampling | Equalises per-interval estimation terms under a fixed budget (heuristic) | Demand map m(θ) is a faithful proxy of local difficulty | Eq. (5), Appendix C.3 |
| Bayesian calibration (Stage 2) | Posterior approximation error O(N^{−1/2}) | A1 bounded likelihood; A2 compact parameter space | [35, 32] |
| Attention weighting (Stage 3) | Weighted bridge risk bound with Σ_k w_k d_{HΔH}(B_k, D_T) | Bounded loss; i.i.d. bridge samples within each domain | [34], Appendix C.2 |
| Adversarial alignment (Stage 3) | Minimises the empirical H-divergence between bridge and target | Sufficient capacity and overlap between bridge and target supports | [19, 21] |

## 3.8 Physical-consistency loss: definition, gradient path and scope

The physical-consistency loss penalises violations of analytically computable spectral constraints. Let Θ collect the trainable parameters of the feature extractor, the attention module and the diagnostic head, and let Ê_Θ(f_c) denote the attention-weighted band energy that the network assigns to a characteristic-frequency band centred at f_c. For each constraint c in a constraint set C, the loss is

L_phy(Θ) = Σ_{c ∈ C} w_c · ( Ê_Θ(f_c) / E_c^{ref} − 1 )²    (11)

where E_c^{ref} > 0 is the analytically predicted reference energy of that band, computed from the simulator geometry and the instantaneous operating point, and w_c is a fixed positive weight. The constraint set C contains, for rolling-element bearings, the band energies at the BPFI, BPFO, BSF and FTF orders computed from the bearing geometry of Appendix B; for gear meshes, the gear-mesh frequency GMF = z·f_r and its first sidebands at ±f_r, with z the tooth count; for coupling misalignment, the 2× running-speed order; and for imbalance, the 1× order. Broadband signatures without discrete characteristic frequencies — most notably propeller cavitation — are explicitly outside the scope of L_phy, and this exclusion is stated rather than absorbed silently: the loss is applied to all scenarios, but the constraint set for cavitation-containing classes is empty, so L_phy reduces to its bearing and gear terms there.

Gradient path. All quantities in Eq. (11) are differentiable with respect to Θ. The gradient flows as ∂L_phy/∂Θ = Σ_c 2w_c ( Ê_Θ(f_c)/E_c^{ref} − 1 ) · (1/E_c^{ref}) · ∂Ê_Θ(f_c)/∂Θ, where ∂Ê_Θ/∂Θ propagates through the differentiable attention weights of Eq. (9) and the feature maps of the ResCNN. The reference energies E_c^{ref} are computed analytically from the simulator's fault model and the measured rotational speed; they are constants with respect to Θ and receive no gradient. The loss therefore trains only the network parameters, and it never updates the simulator or the particle-filter state.

The physical-consistency loss as defined applies to bearing, gear, misalignment and imbalance fault physics; it does not encode fault-coupling physics (for example the interaction of misalignment with bearing wear), which is one reason composite faults remain the weakest class in Section 5.4.
