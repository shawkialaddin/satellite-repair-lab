# Focused related-work review

Checked 16 October 2026 (Riyadh). This is a targeted review, not a systematic review and not a proof that no overlapping work exists. Primary publisher pages, institutional reports, and accessible paper sections were inspected. No claim of having exhaustively read all cited works is made.

Search families included autonomous vulnerability repair, satellite code repair, onboard self-healing, runtime assurance/Simplex, CubeSat runtime verification, and spacecraft update mechanisms. Unrelated Red Hat Satellite results were excluded. Vendor claims were not used to establish research priority.

| Source | Evidence inspected | Relevance and distinction |
| --- | --- | --- |
| [PatchAgent, USENIX Security 2025](https://www.usenix.org/conference/usenixsecurity25/presentation/yu-zheng) | Paper setup, model/cost table, and limitations | Integrates localization, generation, and validation. Its 92.13% figure is a union across models, not a result for one local model. Existing tests have acknowledged limitations. Our small host pilot is not a reproduction or direct performance comparison. |
| [SoK: Towards Effective Automated Vulnerability Repair, USENIX Security 2025](https://www.usenix.org/conference/usenixsecurity25/presentation/li-ying) | Publisher summary and paper | Establishes a broad repair landscape. Combining a generator and verifier is insufficient novelty. |
| [Zhang et al., IWSPA 2024](https://www.nist.gov/publications/evaluating-large-language-models-real-world-vulnerability-repair-cc-code) | NIST bibliographic record and abstract | C/C++ repair study with 223 snippets; localized and semantically complex fixes differ. Does not establish our local-model feasibility. |
| [PHOENIX, arXiv:2608.07126v1](https://arxiv.org/html/2608.07126v1) | Architecture and limitations | Relevant onboard SLM fault-management proposal. Reports data-pipeline/cache work and leaves end-to-end training/recovery evaluation incomplete. Fault-recovery commands differ from synthesized security-code patches. The arXiv record reports conference acceptance; we cite the accessible version. |
| [Aurandt, Jones, and Rozier, CySat-I runtime recovery](https://par.nsf.gov/servlets/purl/10387033) | Paper architecture, fault injection, results | Runtime verification triggers predefined recovery in mock launches. Strong prior evidence for autonomous satellite fault handling; not generation of new security patches. |
| [Slagel et al., Runtime Assurance of Autonomous UAS, 2024](https://ntrs.nasa.gov/citations/20240007986) | NTRS record and author manuscript | Trusted monitors and fallback around untrusted components already have formal foundations. Our Python policy and tests do not provide those proofs. |
| [RTAEval, arXiv:2306.04585](https://arxiv.org/abs/2306.04585) | Abstract and full HTML | Evaluates alternative runtime-assurance logics. Workload-aware comparisons alone do not establish a new assurance architecture. |
| [Lopez and de Fitero, ESA ADCSS 2024 program](https://indico.esa.int/event/532/timetable/?view=standard) | Institutional program abstract | Describes fine-tuned Llama 3 repair from static-analysis findings in a space-software development setting, with a CI/CD extension. We must distinguish in-orbit disconnected generation from ground development tools. Slides were not retrieved, so no slide-specific results are asserted. |
| [SwRI secure micropatching demonstration, 2023](https://www.swri.org/newsroom/press-releases/swri-micropatch-algorithm-improves-ground-spacecraft-software-update-efficiency) | Institutional report | ISS demonstration of efficient update/file repair. Refutes an absolute claim that post-launch patching is impossible; does not demonstrate our generator. |
| [ESA OPS-SAT architecture, 2019](https://www.esa.int/Enabling_Support/Operations/Sandbox_satellite_to_test_operations_innovations_in_space) | Mission description | Experimental Linux payload computer with separate recovery computer. Supports an architectural motivation, not performance equivalence with our host. |
| [NASA Small Spacecraft Avionics, 2026](https://www.nasa.gov/smallsat-institute/sst-soa/small-spacecraft-avionics/) | Avionics overview and software references | Hardware/software stacks vary. Do not treat arbitrary host limits as representative flight-computer specifications. |
| [Qwen2.5-Coder technical report](https://arxiv.org/abs/2409.12186) | Model-series report and official model repositories | Model provenance for the 0.5B/1.5B exploratory runs. Published general coding scores are not repair results for this benchmark. |

## Contribution supported at this stage

An open host testbed and exploratory evidence about bounded local patch generation, separate acceptance policies, and the limits of a small synthetic benchmark. It is premature to claim a first autonomous satellite repair agent, a new runtime-assurance paradigm, or a demonstrated mission-safety improvement.

## Review still needed for a full empirical paper

Backward/forward citation expansion; embedded and binary repair; repair scheduling and runtime adaptation; signed/recoverable updates; real flight-software vulnerability cases; and comparison to reproducible established repair systems. These gaps remain explicit rather than being filled with assumptions.
