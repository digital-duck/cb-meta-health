"""Author cb-meta-health chapter graphs; computes tiers, validates, writes graph.yaml + catalog.json."""
import json
from pathlib import Path

import yaml

class Folded(str):
    """A defines value, emitted as a folded block scalar (>-) instead of a quoted string."""


yaml.add_representer(Folded, lambda d, v: d.represent_scalar("tag:yaml.org,2002:str", v, style=">"))

# Content translations (chapter names/descriptions + per-language concept
# labels) live in locales/content.yaml — see docs/DEV/readme-i18n.md §2a.
CONTENT = yaml.safe_load((Path(__file__).resolve().parents[2] / "locales" / "content.yaml").read_text(encoding="utf-8"))
LABELS = CONTENT["concepts"]
DOMAINS = CONTENT["domains"]
SOURCE_LANG = CONTENT.get("_meta", {}).get("source", "en")

ROOT = Path("/home/gongai/projects/digital-duck/cb-meta-health/public/domains")

# Each chapter: meta + P (primitives: name -> defines), C/A (name -> (defines, prereqs))
CH = []

# ---------------------------------------------------------------- ch01
CH.append(dict(
    id="meta_health_ch01", tag="tcm", capstone="five_phase_body_map",
    P={
        "yin_yang": "Yin-yang (阴阳): the paired, mutually dependent and mutually transforming opposites (rest/activity, cool/warm, substance/function) that TCM uses to describe every process in the body.",
        "qi": "Qi (气): the TCM notion of vital activity — the moving, warming, protecting and transforming function of the body; roughly 'physiological function in motion'.",
        "blood_xue": "Blood (血): in TCM, the nourishing and moistening substance that circulates in the vessels, overlapping with but broader than the anatomical blood.",
        "body_fluids_jinye": "Body fluids (津液): all normal fluids of the body — thin fluids (津) that moisten skin and muscles and thick fluids (液) that lubricate joints, organs and orifices.",
        "essence_jing": "Essence (精): the stored, constitutional substance underlying growth, reproduction and aging, inherited from parents and replenished by food.",
        "spirit_shen": "Spirit (神): the TCM term for consciousness, mental activity and vitality as it shows in the eyes, face and behavior.",
        "five_phases_wuxing": "The Five Phases (五行 — Wood 木, Fire 火, Earth 土, Metal 金, Water 水): five categories of process used to classify and relate natural and bodily phenomena.",
        "meridian_jingluo": "Meridians (经络): the TCM network of channels through which qi and blood are said to flow, linking organs with the surface of the body and the limbs.",
    },
    C={
        "qi_blood_relationship": ("The mutual dependence of qi and blood — 'qi is the commander of blood, blood is the mother of qi' (气为血之帅，血为气之母): qi moves blood, blood nourishes qi.", ["qi", "blood_xue"]),
        "three_treasures_jing_qi_shen": ("The Three Treasures (精气神): essence, qi and spirit as three levels of vitality that cultivation practices aim to conserve and refine.", ["essence_jing", "qi", "spirit_shen"]),
        "generating_cycle_xiangsheng": ("The generating cycle (相生): Wood → Fire → Earth → Metal → Water → Wood, each phase nourishing the next like a mother feeding a child.", ["five_phases_wuxing"]),
        "controlling_cycle_xiangke": ("The controlling cycle (相克): Wood → Earth → Water → Fire → Metal → Wood, each phase restraining another so that no phase grows unchecked.", ["five_phases_wuxing"]),
        "overacting_and_insulting": ("Pathological distortions of the controlling cycle — overacting (相乘, excessive restraint) and insulting (相侮, reversed restraint) — used in TCM to explain how imbalance spreads between organs.", ["controlling_cycle_xiangke"]),
        "five_zang_organs": ("The five zang organs (五脏 — Liver 肝, Heart 心, Spleen 脾, Lung 肺, Kidney 肾): functional systems that store qi, blood and essence, each governed by one of the Five Phases; not identical to the anatomical organs of the same name.", ["five_phases_wuxing", "qi", "blood_xue", "essence_jing"]),
        "six_fu_organs": ("The six fu organs (六腑 — gallbladder, small intestine, stomach, large intestine, bladder, triple burner): hollow organs that receive, transform and pass on food and fluids.", ["five_zang_organs", "body_fluids_jinye"]),
        "zang_fu_pairing": ("Interior-exterior pairing (表里): each zang organ paired with a fu organ and linked by meridians, e.g. Spleen–Stomach, Liver–Gallbladder, Lung–Large Intestine.", ["five_zang_organs", "six_fu_organs", "meridian_jingluo"]),
        "twelve_primary_meridians": ("The twelve primary meridians (十二经脉), each belonging to a zang or fu organ, running along the arms, legs and trunk — e.g. the Lung meridian (手太阴肺经) across the upper chest to the thumb and the Kidney meridian (足少阴肾经) from the sole of the foot.", ["zang_fu_pairing", "meridian_jingluo"]),
        "five_phase_correspondences": ("The Five-Phase correspondence table (五行归类): each phase links an organ, season, emotion, flavor, color, sense organ and tissue — e.g. Wood ↔ Liver ↔ spring ↔ anger ↔ sour ↔ green ↔ eyes ↔ tendons.", ["five_zang_organs", "generating_cycle_xiangsheng"]),
        "triple_burner_sanjiao": ("The triple burner (三焦): the upper (heart, lung), middle (spleen, stomach) and lower (liver, kidney, bladder, intestines) burners, understood as the passageways of qi and fluids through the trunk.", ["six_fu_organs", "body_fluids_jinye", "qi"]),
        "dantian": ("Dantian (丹田): the 'elixir fields', especially the lower dantian a few finger-widths below the navel, used in qigong as the center where attention and breath settle qi.", ["qi", "essence_jing"]),
        "prenatal_postnatal_qi": ("Prenatal (先天) and postnatal (后天) foundations: the Kidney stores inherited essence, while the Spleen and Stomach make new qi and blood from food and drink every day.", ["five_zang_organs", "essence_jing"]),
        "qi_stagnation_blood_stasis": ("Qi stagnation and blood stasis (气滞血瘀): the TCM picture of impaired flow — when qi stops moving freely, blood and fluids pool, which is said to cause distension, pain and dysfunction.", ["qi_blood_relationship"]),
        "heart_kidney_interaction": ("Heart–Kidney interaction (心肾相交, 水火既济): Heart Fire descends to warm Kidney Water and Kidney Water ascends to cool Heart Fire; failure is described as 'Heart Fire flaring upward' (心火上炎).", ["five_zang_organs", "controlling_cycle_xiangke", "yin_yang"]),
        "liver_spleen_relationship": ("The Liver–Spleen relationship (木克土): the Liver's smooth flow of qi supports digestion, and when the Liver is constrained it 'overacts' on the Spleen and Stomach (肝木克脾土).", ["five_zang_organs", "overacting_and_insulting"]),
        "harmony_as_health": ("Health as dynamic balance (阴平阳秘): TCM defines health as yin-yang equilibrium and free flow among the Five Phases, not the absence of a single disease.", ["yin_yang", "generating_cycle_xiangsheng", "controlling_cycle_xiangke", "qi_stagnation_blood_stasis", "three_treasures_jing_qi_shen"]),
    },
    A={
        "five_phase_body_map": ("Using the Five-Phase table, the three burners, the dantian and the prenatal/postnatal roots to read the body as one connected system — linking an everyday sign (e.g. irritability with a poor appetite) to organ relationships and the generating and controlling cycles.", ["five_phase_correspondences", "twelve_primary_meridians", "harmony_as_health", "liver_spleen_relationship", "heart_kidney_interaction", "triple_burner_sanjiao", "dantian", "prenatal_postnatal_qi"]),
    },
))

# ---------------------------------------------------------------- ch02
CH.append(dict(
    id="meta_health_ch02", tag="physiology", capstone="dual_lens_translation",
    P={
        "respiration_mechanics": "Breathing mechanics: the diaphragm and intercostal muscles change rib-cage and thoracic volume to move air in and out of the lungs.",
        "cardiac_output": "Cardiac output: the volume of blood the heart pumps per minute (heart rate × stroke volume), about 5 L/min at rest in adults.",
        "skeletal_muscle_contraction": "Skeletal muscle contraction: voluntary muscles shorten and produce force when activated by motor nerves, then relax.",
        "autonomic_nervous_system": "The autonomic nervous system: the involuntary control system for heart rate, blood vessels, digestion and breathing, with sympathetic and parasympathetic branches.",
        "fascia": "Fascia: the continuous connective-tissue web that wraps and links muscles, organs and bones throughout the body.",
        "joint_range_of_motion": "Joint range of motion: how far a joint can move in each direction (flexion, extension, rotation, lateral bending), limited by bones, ligaments and muscles.",
        "lymphatic_system": "The lymphatic system: a low-pressure network of vessels that returns tissue fluid to the blood and carries immune cells; it has no central pump.",
    },
    C={
        "diaphragmatic_breathing": ("Diaphragmatic ('belly') breathing: slow breathing led by the diaphragm, which expands the lower ribs and abdomen and is linked to parasympathetic activation.", ["respiration_mechanics", "autonomic_nervous_system"]),
        "thoracic_mobility": ("Thoracic mobility: the ability of the rib cage and upper-back spine to extend, rotate and side-bend, which affects posture and how deeply one can breathe.", ["joint_range_of_motion", "respiration_mechanics"]),
        "tidal_volume_and_gas_exchange": ("Tidal volume and gas exchange: how much air each breath moves, and how breathing depth and rate affect oxygen and CO2 exchange in the alveoli.", ["respiration_mechanics"]),
        "regional_blood_flow_distribution": ("Regional blood-flow distribution: the autonomic nervous system redistributes cardiac output among muscles, gut, skin and brain by constricting or dilating vessels, according to what the body is doing.", ["cardiac_output", "autonomic_nervous_system"]),
        "venous_return": ("Venous return: blood flowing back to the heart through low-pressure veins with one-way valves, which sets how much the heart can pump out.", ["cardiac_output"]),
        "skeletal_muscle_pump": ("The skeletal-muscle pump: contracting leg muscles, especially the calf ('second heart'), squeeze the veins and push blood back toward the heart.", ["skeletal_muscle_contraction", "venous_return"]),
        "respiratory_pump": ("The respiratory pump: pressure changes from diaphragmatic breathing help draw venous blood and lymph from the abdomen into the chest.", ["diaphragmatic_breathing", "venous_return"]),
        "lymph_flow": ("Lymph flow: because lymph has no heart, it relies on muscle contraction, breathing and movement, which is why inactivity lets fluid pool in the tissues.", ["lymphatic_system", "skeletal_muscle_pump", "respiratory_pump"]),
        "sympathetic_parasympathetic_balance": ("Sympathetic–parasympathetic balance: 'fight-or-flight' (sympathetic) versus 'rest-and-digest' (parasympathetic) activity, and the body's ability to shift between them.", ["autonomic_nervous_system"]),
        "vagal_tone_and_hrv": ("Vagal tone and heart-rate variability (HRV): beat-to-beat variation in heart rate, an indirect index of parasympathetic (vagus nerve) activity that slow breathing tends to raise.", ["sympathetic_parasympathetic_balance", "diaphragmatic_breathing"]),
        "intra_abdominal_pressure": ("Intra-abdominal pressure: the pressure in the abdominal cavity created by the diaphragm, abdominal wall and pelvic floor working together; it stabilizes the spine and changes with breathing and twisting.", ["diaphragmatic_breathing", "skeletal_muscle_contraction"]),
        "core_stability": ("Core stability: controlling the trunk under movement by coordinating the deep abdominal, back and pelvic-floor muscles with intra-abdominal pressure.", ["intra_abdominal_pressure", "joint_range_of_motion"]),
        "myofascial_lines": ("Myofascial lines: chains of muscle and fascia running the length of the body (e.g. the superficial back line, lateral line and spiral line), so a stretch in one region loads tissue far away.", ["fascia", "skeletal_muscle_contraction"]),
        "spinal_rotation_and_lateral_flexion": ("Spinal rotation and lateral flexion: twisting and side-bending the trunk, which mobilizes the thoracic spine and ribs and loads the spiral and lateral lines.", ["thoracic_mobility", "myofascial_lines"]),
        "posterior_chain": ("The posterior chain: calves, hamstrings, glutes and spinal erectors working as one line, extending the body upward and stabilizing the lower back.", ["myofascial_lines", "skeletal_muscle_contraction"]),
        "squat_mechanics": ("Squat mechanics: hip, knee and ankle bending together with a stable trunk; large leg muscles do the work, so squatting raises heart rate and venous return.", ["joint_range_of_motion", "core_stability", "posterior_chain", "skeletal_muscle_pump"]),
        "tension_relaxation_cycling": ("Tension–relaxation cycling: alternating brief contraction with full release, which pumps blood and lymph more effectively than holding a static position.", ["skeletal_muscle_pump", "regional_blood_flow_distribution"]),
        "interoception": ("Interoception: awareness of internal bodily signals (heartbeat, breath, fullness, tension), which slow mindful movement and eating practice and sharpen.", ["vagal_tone_and_hrv"]),
    },
    A={
        "dual_lens_translation": ("Translating TCM statements into physiology and back — e.g. 'moving Lung qi' ↔ thoracic expansion and gas exchange, 'Kidney root' ↔ calf pump and posterior chain — while noting where the correspondence is mechanistic, where it is plausible, and where it is metaphorical.", ["tidal_volume_and_gas_exchange", "lymph_flow", "vagal_tone_and_hrv", "spinal_rotation_and_lateral_flexion", "squat_mechanics", "tension_relaxation_cycling", "interoception"]),
    },
))

# ---------------------------------------------------------------- ch03
CH.append(dict(
    id="meta_health_ch03", tag="movement", capstone="five_organ_routine_design",
    P={
        "five_phase_correspondences": "The Five-Phase correspondence table (五行归类) linking each phase to an organ, season, emotion, flavor and tissue (from Chapter 1).",
        "generating_cycle_xiangsheng": "The generating cycle (相生): Wood → Fire → Earth → Metal → Water (from Chapter 1).",
        "twelve_primary_meridians": "The twelve primary meridians (十二经脉) and their paths along the limbs and trunk (from Chapter 1).",
        "heart_kidney_interaction": "Heart–Kidney interaction (心肾相交): Heart Fire descends and Kidney Water ascends (from Chapter 1).",
        "dantian": "The lower dantian (下丹田), the center below the navel where qigong settles breath and attention (from Chapter 1).",
        "thoracic_mobility": "Thoracic mobility: extension, rotation and side-bending of the rib cage and upper back (from Chapter 2).",
        "diaphragmatic_breathing": "Diaphragmatic breathing and its parasympathetic effect (from Chapter 2).",
        "myofascial_lines": "Myofascial lines such as the lateral, spiral and superficial back lines (from Chapter 2).",
        "skeletal_muscle_pump": "The calf and leg skeletal-muscle pump that returns venous blood to the heart (from Chapter 2).",
        "intra_abdominal_pressure": "Intra-abdominal pressure and how breathing and trunk movement change it (from Chapter 2).",
        "squat_mechanics": "Squat mechanics: coordinated hip, knee and ankle flexion over a stable trunk (from Chapter 2).",
    },
    C={
        "yongquan_point": ("Yongquan (涌泉, KI-1), the 'bubbling spring' point on the sole of the foot where the Kidney meridian begins; rising onto the toes and landing on the heels is said to stimulate it.", ["twelve_primary_meridians"]),
        "chest_expansion_kuoxiong": ("Chest expansion (扩胸) → Lung (肺) → Metal (金): opening the arms and chest stretches the pectorals and intercostals and increases thoracic volume; in TCM it opens the Lung meridian across the upper chest and 'draws in clear qi'.", ["thoracic_mobility", "diaphragmatic_breathing", "five_phase_correspondences", "twelve_primary_meridians"]),
        "rib_fanning_shanlei": ("Rib fanning (扇肋) → Liver (肝) → Wood (木): side-bending and spreading the ribs stretches the lateral line, intercostals and obliques around the hypochondrium; in TCM it frees the Liver meridian's flank pathway and relieves Liver qi stagnation (肝气郁结).", ["myofascial_lines", "thoracic_mobility", "five_phase_correspondences", "twelve_primary_meridians"]),
        "body_lifting_tishen": ("Body lifting (提身) → Kidney (肾) → Water (水): reaching up while rising onto the toes engages the posterior chain and calf pump; in TCM it stretches the back line and stimulates Yongquan at the root of the Kidney meridian.", ["skeletal_muscle_pump", "myofascial_lines", "yongquan_point", "five_phase_correspondences"]),
        "torso_twist_niuzhuan": ("Torso twist (扭转) → Spleen (脾) → Earth (土): trunk rotation alternately compresses and releases the abdomen and mobilizes the thoracolumbar fascia; in TCM it 'wrings out' the middle burner and supports the Spleen's transformation (运化). The effect on gut motility is plausible but little studied.", ["intra_abdominal_pressure", "myofascial_lines", "five_phase_correspondences"]),
        "deep_squat_shendun": ("Deep squat (深蹲) → Heart (心) → Fire (火): recruiting the largest leg muscles raises heart rate and venous return; in TCM, lowering the center of gravity leads Heart Fire downward to meet Kidney Water (引火归元).", ["squat_mechanics", "skeletal_muscle_pump", "heart_kidney_interaction", "five_phase_correspondences"]),
        "five_organ_movement_matrix": ("The five-organ movement matrix: one table of movement, main physical action, target organ, phase, and meridian or physiological mechanism for all five exercises.", ["chest_expansion_kuoxiong", "rib_fanning_shanlei", "body_lifting_tishen", "torso_twist_niuzhuan", "deep_squat_shendun"]),
        "generating_cycle_sequence": ("Generating-cycle order (相生顺序): rib fanning (Wood) → deep squat (Fire) → torso twist (Earth) → chest expansion (Metal) → body lifting (Water), so that each movement 'feeds' the next — suited to daily cultivation.", ["five_organ_movement_matrix", "generating_cycle_xiangsheng"]),
        "breath_first_sequence": ("Breath-first order: starting with chest expansion (Lung) because breathing is the easiest bridge from voluntary control to the autonomic nervous system — the order used in some popular teaching videos, differing from the generating cycle only by swapping Lung and Liver.", ["five_organ_movement_matrix", "diaphragmatic_breathing"]),
        "top_to_bottom_sequence": ("Top-to-bottom order: chest → ribs → waist → legs → feet, warming joints from the upper body downward and, in TCM terms, drawing rising yang back to the root.", ["five_organ_movement_matrix", "thoracic_mobility"]),
        "sealing_finish": ("The sealing finish (收势): ending with body lifting and a pause with hands over the lower dantian to 'settle and store' qi, instead of stopping abruptly.", ["body_lifting_tishen", "dantian"]),
        "safe_practice_and_modification": ("Safe practice: pain-free range, knee tracking and partial squats, a chair or wall for balance, gentle twisting for back or disc problems, and no breath-holding for people with high blood pressure.", ["five_organ_movement_matrix", "squat_mechanics"]),
    },
    A={
        "five_organ_routine_design": ("Designing a personal 5–10 minute five-organ routine: choosing a sequencing logic for the goal and time of day, pairing each movement with the breath, ending with the sealing finish, and scaling each movement to one's body.", ["generating_cycle_sequence", "breath_first_sequence", "top_to_bottom_sequence", "sealing_finish", "safe_practice_and_modification"]),
    },
))

# ---------------------------------------------------------------- ch04
CH.append(dict(
    id="meta_health_ch04", tag="movement", capstone="daily_baduanjin_practice_plan",
    P={
        "daoyin_tradition": "Daoyin (导引): the ancient Chinese tradition of guided stretching and breathing exercises for health, of which Baduanjin is a well-known descendant.",
        "triple_burner_sanjiao": "The triple burner (三焦): upper, middle and lower passageways of qi and fluids (from Chapter 1).",
        "heart_kidney_interaction": "Heart–Kidney interaction (心肾相交, 水火既济) (from Chapter 1).",
        "twelve_primary_meridians": "The twelve primary meridians (十二经脉) (from Chapter 1).",
        "dantian": "The lower dantian (下丹田) (from Chapter 1).",
        "diaphragmatic_breathing": "Diaphragmatic breathing (from Chapter 2).",
        "tension_relaxation_cycling": "Tension–relaxation cycling as a circulatory pump (from Chapter 2).",
        "five_organ_movement_matrix": "The five-organ movement matrix — 扩胸, 扇肋, 提身, 扭转, 深蹲 (from Chapter 3).",
        "yongquan_point": "Yongquan (涌泉, KI-1) on the sole of the foot (from Chapter 3).",
        "evidence_quality": "Evidence quality: how to weigh case reports, observational studies, randomized controlled trials and meta-analyses, and why small or unblinded trials can overstate benefits.",
    },
    C={
        "baduanjin_overview": ("Baduanjin (八段锦): a standing qigong routine of eight movements, first recorded in the Song dynasty and standardized in 2003 as a national Health Qigong (健身气功) set; one round takes about 10–12 minutes.", ["daoyin_tradition"]),
        "three_regulations": ("The three regulations (三调): regulating the body (调身, posture), the breath (调息, breathing) and the mind (调心, attention) — together what distinguishes qigong from ordinary calisthenics.", ["baduanjin_overview", "diaphragmatic_breathing"]),
        "form1_hold_up_heavens": ("Form 1 — Holding up the heavens to regulate the triple burner (两手托天理三焦): pressing both palms up stretches the whole trunk and is the opening 'master key' that frees the three burners for the forms that follow.", ["baduanjin_overview", "triple_burner_sanjiao"]),
        "form2_draw_the_bow": ("Form 2 — Drawing the bow to shoot the eagle (左右开弓似射雕): a horse stance with a bow-drawing arm action that opens the chest and stretches the Lung and Large Intestine meridians — the natural counterpart of chest expansion (Lung/Metal).", ["baduanjin_overview", "twelve_primary_meridians"]),
        "form3_single_arm_raise": ("Form 3 — Raising one arm to regulate Spleen and Stomach (调理脾胃须单举): one palm presses up and the other presses down, stretching the abdomen to 'raise the clear and lower the turbid' (升清降浊) in the middle burner.", ["baduanjin_overview", "triple_burner_sanjiao"]),
        "form4_look_back": ("Form 4 — Looking back to cure the five strains and seven injuries (五劳七伤往后瞧): turning the head and upper trunk mobilizes the cervical and thoracic spine; paired with the torso twist (Spleen/Earth).", ["baduanjin_overview", "twelve_primary_meridians"]),
        "form5_sway_head_and_tail": ("Form 5 — Swaying head and tail to clear Heart Fire (摇头摆尾去心火): a deep horse stance with a circling lean of the trunk that lowers the center of gravity to 'lead Heart Fire down' — the compound form of the deep squat (Heart/Fire).", ["baduanjin_overview", "heart_kidney_interaction"]),
        "form6_touch_toes": ("Form 6 — Both hands reach the feet to strengthen Kidney and waist (两手攀足固肾腰): a forward fold with hands sliding down the back of the legs, stretching the Bladder and Kidney meridians and the posterior chain.", ["baduanjin_overview", "twelve_primary_meridians"]),
        "form7_clench_fists_glare": ("Form 7 — Clenching fists with glaring eyes to increase strength (攒拳怒目增气力): punching from a horse stance with a fierce gaze to vent Liver qi — the counterpart of rib fanning (Liver/Wood), since the Liver 'opens into the eyes'.", ["baduanjin_overview", "twelve_primary_meridians"]),
        "form8_heel_bounce": ("Form 8 — Bouncing on the heels seven times to banish illness (背后七颠百病消): rising onto the toes and dropping gently onto the heels jolts the body, works the calf pump and stimulates Yongquan — the direct match for body lifting (Kidney/Water).", ["baduanjin_overview", "yongquan_point"]),
        "breath_movement_coordination": ("Coordinating breath and movement: breathing in as the body rises or opens and out as it sinks or closes, without ever holding the breath.", ["three_regulations"]),
        "tension_release_rhythm": ("The tension–release rhythm (松紧结合): a brief firm moment at the end of each form (pressing up, drawing the bow, clenching) followed by immediate softening — where the circulatory 'pumping' happens.", ["three_regulations", "tension_relaxation_cycling"]),
        "closing_form_shougong": ("Closing the practice (收功): standing still with hands over the lower dantian for three to five slow breaths, rather than sitting down straight away or picking up a phone, to 'store' the qi that has been mobilized.", ["dantian", "form8_heel_bounce", "breath_movement_coordination"]),
        "baduanjin_five_organ_mapping": ("The Baduanjin ↔ five-organ-exercise map: Wood 7 ↔ rib fanning; Fire 5 ↔ deep squat; Earth 4 (and 3) ↔ torso twist; Metal 2 (and 1, 3) ↔ chest expansion; Water 8 (and 6) ↔ body lifting — with form 1 as the overall regulator. The five exercises serve as isolation drills for Baduanjin's compound forms.", ["five_organ_movement_matrix", "form1_hold_up_heavens", "form2_draw_the_bow", "form3_single_arm_raise", "form4_look_back", "form5_sway_head_and_tail", "form6_touch_toes", "form7_clench_fists_glare", "form8_heel_bounce"]),
        "practice_dose": ("Practice dose: about 10 minutes (one or two rounds), once or twice a day — enough to mobilize the body without fatigue or heavy sweating (which TCM says 'consumes qi'); a morning round to raise yang and an evening round to release tension.", ["baduanjin_overview", "three_regulations"]),
        "baduanjin_evidence_base": ("The evidence for Baduanjin: randomized trials and meta-analyses report improvements in balance, flexibility, blood pressure, sleep quality, mood and quality of life, especially in older adults, but many trials are small and unblinded; organ-specific claims remain mostly traditional.", ["baduanjin_overview", "evidence_quality"]),
    },
    A={
        "daily_baduanjin_practice_plan": ("A personal daily Baduanjin plan: the full set with breath coordination and tension–release, organ-targeted extras drawn from the mapping, a proper closing, and realistic expectations based on the evidence.", ["baduanjin_five_organ_mapping", "breath_movement_coordination", "tension_release_rhythm", "closing_form_shougong", "practice_dose", "baduanjin_evidence_base"]),
    },
))

# ---------------------------------------------------------------- ch05
CH.append(dict(
    id="meta_health_ch05", tag="nutrition", capstone="mindful_meal_protocol",
    P={
        "gastrointestinal_tract": "The gastrointestinal tract: mouth, esophagus, stomach, small and large intestine, with the liver and pancreas as accessory organs.",
        "smooth_muscle": "Smooth muscle: involuntary muscle in the gut wall and blood vessels that contracts rhythmically without conscious control.",
        "regional_blood_flow_distribution": "Regional redistribution of cardiac output between muscles and organs (from Chapter 2).",
        "sympathetic_parasympathetic_balance": "Sympathetic ('fight-or-flight') versus parasympathetic ('rest-and-digest') balance (from Chapter 2).",
        "liver_metabolic_role": "The liver's metabolic role: processing nutrients arriving from the gut, storing glycogen, making bile and clearing toxins.",
        "spleen_stomach_system": "The Spleen–Stomach system (脾胃), the Earth phase and middle burner (中焦) of TCM (from Chapter 1).",
        "prenatal_postnatal_qi": "Postnatal qi (后天之气): qi and blood made daily from food by the Spleen and Stomach (from Chapter 1).",
    },
    C={
        "cephalic_phase_digestion": ("The cephalic phase of digestion: the sight, smell and taste of food and the act of chewing trigger saliva, gastric acid and insulin release through the vagus nerve before food reaches the stomach.", ["gastrointestinal_tract", "sympathetic_parasympathetic_balance"]),
        "mastication": ("Mastication (咀嚼): chewing breaks food into small pieces, mixes it with saliva and enzymes, and gives the brain time to register what is being eaten.", ["gastrointestinal_tract", "cephalic_phase_digestion"]),
        "satiety_signaling": ("Satiety signalling: stretch receptors and gut hormones (e.g. CCK, GLP-1, PYY) tell the brain the stomach is filling, with a lag of roughly 15–20 minutes behind the eating itself.", ["gastrointestinal_tract", "mastication"]),
        "splanchnic_circulation": ("The splanchnic circulation: blood supply to the stomach, intestines, pancreas, spleen and liver, which receives roughly a quarter of resting cardiac output.", ["regional_blood_flow_distribution", "gastrointestinal_tract"]),
        "postprandial_hyperemia": ("Postprandial hyperemia (餐后充血): after a meal, intestinal blood flow rises substantially (superior mesenteric flow can roughly double) and cardiac output increases to supply digestion.", ["splanchnic_circulation"]),
        "cardiovascular_load_of_digestion": ("The cardiovascular load of digestion: heart rate and cardiac output rise after large meals, which is why vigorous exercise straight after eating competes for blood and why some older adults feel dizzy after meals (postprandial hypotension).", ["postprandial_hyperemia", "sympathetic_parasympathetic_balance"]),
        "peristalsis_and_motility": ("Peristalsis and gut motility: coordinated smooth-muscle waves that mix and move food along several metres of gut, strengthened by parasympathetic activity and inhibited by stress.", ["smooth_muscle", "sympathetic_parasympathetic_balance", "gastrointestinal_tract"]),
        "hepatic_first_pass_processing": ("First-pass processing in the liver: nutrient-rich blood from the gut goes through the portal vein to the liver first, which stores glucose as glycogen, packages fats and makes bile.", ["liver_metabolic_role", "splanchnic_circulation"]),
        "postprandial_glucose_response": ("The post-meal glucose response: blood sugar rises and falls after eating depending on meal composition, eating speed, gastric emptying and muscle activity; large, repeated spikes are linked to metabolic strain.", ["hepatic_first_pass_processing", "peristalsis_and_motility"]),
        "stomach_receiving_ripening": ("The Stomach receives and ripens (胃主受纳腐熟): in TCM, the Stomach is the vessel that takes in food and 'rots and ripens' it as the first stage of digestion.", ["spleen_stomach_system"]),
        "spleen_transformation_transport": ("The Spleen transforms and transports (脾主运化): the Spleen extracts the refined essence (水谷精微) from food and fluids and distributes it to make qi and blood; this work is powered by Spleen yang (脾阳).", ["spleen_stomach_system", "prenatal_postnatal_qi"]),
        "ascending_clear_descending_turbid": ("Ascending the clear, descending the turbid (升清降浊): Spleen qi lifts nourishment upward while Stomach qi sends waste downward; when this reverses, bloating, belching and heaviness follow.", ["spleen_transformation_transport", "stomach_receiving_ripening"]),
        "eating_as_internal_exercise": ("Eating as internal exercise (饮食即内脏运动): a meal is a demanding workout for the digestive organs and circulation — blood redistributes, smooth muscle works, and the liver's metabolic load surges — equivalent in TCM to firing up the Spleen–Stomach engine. Like any workout, it needs preparation, the right load and recovery.", ["postprandial_hyperemia", "peristalsis_and_motility", "spleen_transformation_transport", "cardiovascular_load_of_digestion"]),
        "digestive_warm_up": ("The digestive warm-up: a few slow breaths and a relaxed start before the first bite, then thorough chewing — shifting into rest-and-digest and letting the cephalic phase prime secretions, like warming up before a workout.", ["eating_as_internal_exercise", "cephalic_phase_digestion", "mastication"]),
        "digestive_load_pacing": ("Pacing the digestive load: eating slowly and stopping at about 70–80% full (七分饱, hara hachi bu) so satiety signals can catch up and the Spleen–Stomach is not overloaded.", ["eating_as_internal_exercise", "satiety_signaling"]),
        "digestive_overtraining": ("Digestive 'overtraining': overeating, bolting food and heavy late meals overload the organs, as overtraining injures muscles — seen in TCM as food stagnation (积食) and a weakened Spleen, and in physiology as reflux, sluggishness and large glucose swings.", ["digestive_load_pacing", "ascending_clear_descending_turbid", "postprandial_glucose_response"]),
        "post_meal_gentle_movement": ("Gentle movement after meals (饭后百步走): an easy walk or gentle forms (e.g. Baduanjin forms 3 and 4) about 10–40 minutes after eating measurably blunts the glucose spike and, in TCM terms, aids transformation; vigorous exercise should wait longer.", ["postprandial_glucose_response", "cardiovascular_load_of_digestion", "ascending_clear_descending_turbid"]),
    },
    A={
        "mindful_meal_protocol": ("The mindful-meal protocol: before (warm-up breaths, no screens), during (thorough chewing, pacing to 70–80% full) and after (rest, then gentle movement) — a practical routine that treats every meal as a well-coached internal workout.", ["digestive_warm_up", "digestive_load_pacing", "digestive_overtraining", "post_meal_gentle_movement"]),
    },
))

# ---------------------------------------------------------------- ch06
CH.append(dict(
    id="meta_health_ch06", tag="nutrition", capstone="five_phase_meal_design",
    P={
        "energy_balance": "Energy balance: energy intake from food versus energy expenditure (basal metabolic rate, digestion and activity), which together determine weight change over time.",
        "macronutrients": "Macronutrients: protein, carbohydrate and fat — the nutrients that supply energy and building material.",
        "micronutrients_and_hydration": "Micronutrients and hydration: vitamins, minerals and water, needed in small amounts as co-factors for metabolism and signalling.",
        "dietary_fiber": "Dietary fiber: plant carbohydrates that human enzymes cannot digest, which add bulk and feed gut bacteria.",
        "gut_microbiome": "The gut microbiome: the trillions of microbes in the large intestine that ferment fiber and influence digestion, immunity and metabolism.",
        "yin_yang": "Yin-yang: complementary opposites such as cool/warm and rest/activity (from Chapter 1).",
        "five_phase_correspondences": "The Five-Phase correspondence table linking organs, flavors, colors and seasons (from Chapter 1).",
        "spleen_transformation_transport": "The Spleen transforms and transports (脾主运化), powered by Spleen yang (from Chapter 5).",
        "circadian_clock": "The circadian clock: the body's roughly 24-hour internal timer, set mainly by light, that schedules hormones, digestion and sleep.",
    },
    C={
        "protein_across_life": ("Protein across the lifespan: adequate, evenly spread protein supports muscle repair and helps prevent age-related muscle loss (sarcopenia), which matters more after about age 50.", ["macronutrients", "energy_balance"]),
        "carbohydrate_quality": ("Carbohydrate quality and glycemic load: whole, fiber-rich carbohydrates raise blood sugar more gently than refined starches and sugars.", ["macronutrients", "dietary_fiber"]),
        "dietary_fat_quality": ("Dietary fat quality: unsaturated fats from nuts, seeds, fish and plant oils versus excess saturated and industrial trans fats.", ["macronutrients"]),
        "fiber_microbiome_axis": ("The fiber–microbiome axis: gut bacteria ferment fiber into short-chain fatty acids that nourish the gut lining and help regulate inflammation and appetite.", ["dietary_fiber", "gut_microbiome"]),
        "whole_vs_ultra_processed_food": ("Whole versus ultra-processed food: the NOVA classification, and why industrial formulations high in refined starch, sugar, fat and additives are linked to overeating and poorer health.", ["carbohydrate_quality", "dietary_fat_quality", "micronutrients_and_hydration"]),
        "four_natures_siqi": ("The four natures (四气): foods classified as cold, cool, neutral, warm or hot by their effect on the body — e.g. watermelon cooling, ginger warming.", ["yin_yang"]),
        "five_flavors_wuwei": ("The five flavors (五味): sour → Liver, bitter → Heart, sweet → Spleen, pungent → Lung, salty → Kidney; each flavor has an action (astringe, drain, tonify, disperse, soften), and any flavor in excess harms its organ.", ["five_phase_correspondences"]),
        "five_colors_foods": ("The five colors (五色): green → Liver, red → Heart, yellow → Spleen, white → Lung, black → Kidney — a simple TCM cue for variety that lines up with modern advice to 'eat the rainbow'.", ["five_phase_correspondences"]),
        "warm_cooked_food_principle": ("The warm, cooked food principle: TCM holds that habitual cold, raw and iced food weakens Spleen yang, and favours warm, cooked, easily digested meals such as congee, soups and steamed vegetables.", ["four_natures_siqi", "spleen_transformation_transport"]),
        "dampness_and_phlegm": ("Dampness and phlegm (湿, 痰浊): in TCM, what builds up when the Spleen cannot transform an excess of greasy, sweet, rich or cold food — heaviness, bloating, sluggishness — which some authors compare with metabolic overload.", ["spleen_transformation_transport", "whole_vs_ultra_processed_food"]),
        "junk_load": ("'Junk load' (劣质食物 = 垃圾训练): low-quality food makes the digestive organs work hard for little nourishment — the internal equivalent of training with bad form under a heavy, useless load.", ["whole_vs_ultra_processed_food", "dampness_and_phlegm"]),
        "meal_timing_chrononutrition": ("Meal timing and chrononutrition: the same meal is handled better earlier in the day, and late-night eating conflicts with the circadian clock — 'forcing the organs to work overtime'.", ["energy_balance", "circadian_clock"]),
        "balanced_plate": ("The balanced plate: roughly half vegetables and fruit, a quarter whole grains, a quarter protein, plus healthy fats — cross-checked against the five colors for variety.", ["protein_across_life", "carbohydrate_quality", "dietary_fat_quality", "fiber_microbiome_axis", "five_colors_foods"]),
        "food_as_medicine_shiliao": ("Food as medicine (药食同源, 食疗): everyday foods with recognized TCM actions — ginger, Chinese yam, jujube, goji, mung bean — used gently and seasonally, not as a substitute for medical treatment.", ["four_natures_siqi", "five_flavors_wuwei"]),
        "constitution_based_eating": ("Eating for one's constitution (体质): the nine TCM constitution types (e.g. qi-deficient, yang-deficient, damp-heat) and how the same food can suit one person and not another.", ["four_natures_siqi", "dampness_and_phlegm", "food_as_medicine_shiliao"]),
    },
    A={
        "five_phase_meal_design": ("Designing a week of meals that satisfy both lenses: a balanced plate, whole foods, all five colors and flavors in moderation, warm cooked foods, sensible timing, and adjustments for one's constitution.", ["balanced_plate", "junk_load", "warm_cooked_food_principle", "five_flavors_wuwei", "meal_timing_chrononutrition", "constitution_based_eating"]),
    },
))

# ---------------------------------------------------------------- ch07
CH.append(dict(
    id="meta_health_ch07", tag="mind", capstone="stress_resilience_routine",
    P={
        "hpa_axis": "The HPA axis (hypothalamus–pituitary–adrenal): the hormonal stress system that releases cortisol.",
        "sympathetic_parasympathetic_balance": "Sympathetic versus parasympathetic balance (from Chapter 2).",
        "vagal_tone_and_hrv": "Vagal tone and heart-rate variability (from Chapter 2).",
        "diaphragmatic_breathing": "Diaphragmatic breathing (from Chapter 2).",
        "postprandial_hyperemia": "Post-meal redistribution of blood to the gut (from Chapter 5).",
        "five_phase_correspondences": "The Five-Phase correspondence table, including the five emotions (from Chapter 1).",
        "qi_stagnation_blood_stasis": "Qi stagnation and blood stasis (气滞血瘀) (from Chapter 1).",
        "liver_spleen_relationship": "The Liver–Spleen relationship (木克土) (from Chapter 1).",
        "liver_opening_movements": "Liver-opening movements: rib fanning (扇肋) and Baduanjin form 7 (攒拳怒目) (from Chapters 3–4).",
    },
    C={
        "acute_vs_chronic_stress": ("Acute versus chronic stress: a short stress response mobilizes energy and resolves, whereas a stress response that stays switched on keeps cortisol and sympathetic tone elevated.", ["hpa_axis", "sympathetic_parasympathetic_balance"]),
        "allostatic_load": ("Allostatic load: the cumulative 'wear and tear' of repeated or chronic stress on blood pressure, metabolism, sleep and immunity.", ["acute_vs_chronic_stress"]),
        "stress_and_digestion": ("Stress and digestion: fight-or-flight activity constricts gut blood vessels, slows motility and cuts digestive secretions — so eating while stressed means the internal workout starts under-supplied.", ["acute_vs_chronic_stress", "postprandial_hyperemia"]),
        "gut_brain_axis": ("The gut–brain axis: two-way communication between gut and brain through the vagus nerve, hormones, immune signals and the microbiome.", ["stress_and_digestion", "vagal_tone_and_hrv"]),
        "seven_emotions_qiqing": ("The seven emotions (七情 — joy, anger, worry, pensiveness, grief, fear, fright): normal emotions that TCM holds become causes of illness when intense or prolonged.", ["five_phase_correspondences"]),
        "five_emotions_five_organs": ("The five emotions and five organs: anger harms the Liver, excess joy the Heart, overthinking the Spleen, grief the Lung, fear the Kidney (怒伤肝, 喜伤心, 思伤脾, 悲伤肺, 恐伤肾).", ["seven_emotions_qiqing", "five_phase_correspondences"]),
        "liver_free_flow_shuxie": ("The Liver governs free flow (肝主疏泄): the Liver keeps qi moving smoothly, which in turn regulates emotion, digestion and the menstrual cycle.", ["five_emotions_five_organs", "qi_stagnation_blood_stasis"]),
        "liver_qi_stagnation": ("Liver qi stagnation (肝气郁结): frustration or suppressed emotion blocks the Liver's free flow, felt as sighing, tight flanks, irritability and a lump in the throat.", ["liver_free_flow_shuxie"]),
        "wood_overacting_on_earth": ("Wood overacting on Earth (肝木克脾土, 肝脾不调): stuck Liver qi attacks the Spleen and Stomach, causing bloating, poor appetite or stress-related bowel upset — TCM's counterpart of stress shutting down digestion.", ["liver_qi_stagnation", "liver_spleen_relationship", "stress_and_digestion"]),
        "emotional_eating": ("Emotional eating: eating to soothe stress or boredom, overriding satiety — 'overthinking harms the Spleen' in TCM, reward-driven eating in modern terms.", ["gut_brain_axis", "wood_overacting_on_earth"]),
        "breath_as_bridge": ("Breath as the bridge: breathing is the one autonomic function under voluntary control, so slow breathing (around 6 breaths per minute) is the quickest way to shift from sympathetic to parasympathetic tone.", ["diaphragmatic_breathing", "vagal_tone_and_hrv"]),
        "releasing_liver_qi_through_movement": ("Releasing Liver qi through movement: flank stretching, rib fanning and the glaring-fist form give stagnant qi an outlet — physically they loosen the trunk and discharge tension.", ["liver_qi_stagnation", "liver_opening_movements"]),
        "mind_regulation_tiaoxin": ("Regulating the mind (调心): single-pointed attention on breath or the lower dantian (意守丹田), the mental half of qigong and mindful eating.", ["breath_as_bridge"]),
        "hrv_self_monitoring": ("Monitoring stress with HRV: using resting heart rate and HRV from a wearable, together with sleep and mood, as simple feedback on accumulated load and recovery.", ["vagal_tone_and_hrv", "allostatic_load"]),
    },
    A={
        "stress_resilience_routine": ("A daily stress-resilience routine: three slow breaths before each meal, a liver-releasing movement when tension builds, a calm evening wind-down, and HRV or journal feedback — protecting digestion from 'Wood overacting on Earth'.", ["wood_overacting_on_earth", "emotional_eating", "breath_as_bridge", "releasing_liver_qi_through_movement", "mind_regulation_tiaoxin", "hrv_self_monitoring"]),
    },
))

# ---------------------------------------------------------------- ch08
CH.append(dict(
    id="meta_health_ch08", tag="rhythms", capstone="personal_daily_rhythm_schedule",
    P={
        "circadian_clock": "The circadian clock: the body's roughly 24-hour internal timer (suprachiasmatic nucleus and peripheral clocks).",
        "yin_yang": "Yin-yang (from Chapter 1).",
        "five_phase_correspondences": "The Five-Phase correspondence table, including the five seasons (from Chapter 1).",
        "twelve_primary_meridians": "The twelve primary meridians (from Chapter 1).",
    },
    C={
        "light_entrainment": ("Light entrainment: morning daylight sets the circadian clock, while bright or blue light late at night delays it.", ["circadian_clock"]),
        "cortisol_melatonin_rhythm": ("The cortisol–melatonin rhythm: cortisol peaks soon after waking to mobilize energy, and melatonin rises in the evening darkness to prepare for sleep.", ["circadian_clock"]),
        "sleep_architecture": ("Sleep architecture: repeating ~90-minute cycles of light, deep (slow-wave) and REM sleep; deep sleep dominates early in the night and REM toward the morning.", ["circadian_clock"]),
        "sleep_and_metabolic_repair": ("Sleep and metabolic repair: tissue repair and growth-hormone release happen in deep sleep, and short sleep impairs glucose tolerance and raises appetite hormones.", ["sleep_architecture", "cortisol_melatonin_rhythm"]),
        "chrononutrition": ("Chrononutrition: insulin sensitivity is higher earlier in the day, so front-loading meals and finishing eating a few hours before bed suits the circadian clock.", ["cortisol_melatonin_rhythm", "sleep_and_metabolic_repair"]),
        "exercise_timing": ("Exercise timing: morning movement in daylight helps set the clock and 'raise yang'; calmer practice suits the evening, and vigorous exercise close to bedtime can delay sleep.", ["light_entrainment", "cortisol_melatonin_rhythm"]),
        "day_night_yin_yang": ("Day–night yin-yang (昼夜阴阳消长): yang grows from midnight to noon and yin grows from noon to midnight, so activity belongs to the day and storage and rest to the night.", ["yin_yang", "circadian_clock"]),
        "organ_clock_ziwu_liuzhu": ("The meridian organ clock (子午流注): twelve two-hour periods, each assigned to a meridian — Lung 3–5, Large Intestine 5–7, Stomach 7–9, Spleen 9–11, Heart 11–13, Small Intestine 13–15, Bladder 15–17, Kidney 17–19, Pericardium 19–21, Triple Burner 21–23, Gallbladder 23–1, Liver 1–3.", ["twelve_primary_meridians", "day_night_yin_yang"]),
        "sleep_before_zishi": ("Sleeping before 子时 (23:00): TCM advises being asleep during the Gallbladder and Liver hours, when 'blood returns to the Liver when one lies down' (人卧则血归于肝) — in line with modern advice to keep a regular early bedtime.", ["organ_clock_ziwu_liuzhu", "sleep_architecture"]),
        "breakfast_in_chenshi": ("Breakfast in 辰时 (7–9 a.m., Stomach time): the organ clock and chrononutrition agree that a real breakfast should anchor the day's eating.", ["organ_clock_ziwu_liuzhu", "chrononutrition"]),
        "four_seasons_regimen": ("The four-seasons regimen (四时养生): spring for growth, summer for expansion, autumn for gathering, winter for storing (春生夏长秋收冬藏) — adjusting sleep, activity and diet to the season.", ["five_phase_correspondences", "day_night_yin_yang"]),
        "seasonal_organ_care": ("Caring for the organ of each season: nourish the Liver in spring, Heart in summer, Spleen in late summer, Lung in autumn and Kidney in winter (春养肝, 夏养心, 长夏养脾, 秋养肺, 冬养肾).", ["four_seasons_regimen", "five_phase_correspondences"]),
        "seasonal_food_and_movement": ("Seasonal food and movement: lighter, cooling foods and early mornings in summer; warming, nourishing foods and gentler, shorter practice in winter; emphasizing the season's organ exercise.", ["seasonal_organ_care", "exercise_timing", "chrononutrition"]),
    },
    A={
        "personal_daily_rhythm_schedule": ("A personal rhythm plan: a 24-hour day (morning light and Baduanjin, breakfast in 辰时, main meal at midday, gentle movement after meals, an early light dinner, an evening wind-down, sleep before 23:00) adjusted through the year according to the season's phase and organ.", ["light_entrainment", "exercise_timing", "breakfast_in_chenshi", "sleep_before_zishi", "sleep_and_metabolic_repair", "seasonal_food_and_movement"]),
    },
))

# ---------------------------------------------------------------- ch09
CH.append(dict(
    id="meta_health_ch09", tag="integration", capstone="daily_meta_health_protocol",
    P={
        "harmony_as_health": "Health as dynamic balance (阴平阳秘) (from Chapter 1).",
        "dual_lens_translation": "Translating between TCM and physiology (from Chapter 2).",
        "five_organ_routine_design": "A personal five-organ exercise routine (from Chapter 3).",
        "daily_baduanjin_practice_plan": "A daily Baduanjin practice plan (from Chapter 4).",
        "eating_as_internal_exercise": "Eating as internal exercise (饮食即内脏运动) (from Chapter 5).",
        "mindful_meal_protocol": "The mindful-meal protocol (from Chapter 5).",
        "five_phase_meal_design": "Five-Phase meal design (from Chapter 6).",
        "stress_resilience_routine": "The stress-resilience routine (from Chapter 7).",
        "personal_daily_rhythm_schedule": "The personal 24-hour rhythm (from Chapter 8).",
        "evidence_quality": "Evidence quality: weighing trials, observational data and tradition (from Chapter 4).",
    },
    C={
        "internal_external_cultivation": ("Internal-external cultivation (内外兼修): external movement guides qi and blood through the channels while mindful eating conditions the organs from within — two halves of one practice.", ["eating_as_internal_exercise", "daily_baduanjin_practice_plan", "mindful_meal_protocol"]),
        "mind_body_digestive_loop": ("The mind–body–digestive loop: mental state → mindful eating → post-meal rest → gentle guiding movement → better mental state; stress breaks the loop at its first link.", ["internal_external_cultivation", "stress_resilience_routine"]),
        "five_phase_integration_matrix": ("The Five-Phase integration matrix: for each phase, one row linking organ, five-organ exercise, Baduanjin form, flavor and food, emotion, organ-clock time and season — the whole book in one table.", ["five_organ_routine_design", "daily_baduanjin_practice_plan", "five_phase_meal_design", "stress_resilience_routine", "personal_daily_rhythm_schedule"]),
        "organ_training_principles": ("Training principles for the organs: warm-up, appropriate load, progression, recovery and consistency — 'train, don't overload' — applied equally to muscles, the digestive organs and the nervous system.", ["eating_as_internal_exercise", "harmony_as_health"]),
        "habit_formation": ("Habit formation: small daily doses (10 minutes, one breath before each meal) anchored to existing routines such as meals and waking are more durable than ambitious programs.", ["organ_training_principles"]),
        "personalization": ("Personalization: adjusting the framework for constitution (体质), age, fitness, chronic conditions and culture instead of prescribing one routine for everyone.", ["five_phase_integration_matrix", "organ_training_principles"]),
        "self_observation_feedback": ("Self-observation as feedback: tracking energy, appetite, digestion and stool, sleep, mood, tongue appearance and, optionally, HRV or glucose, to adjust practice the way a coach adjusts training.", ["organ_training_principles", "dual_lens_translation"]),
        "evidence_and_safety_lens": ("The evidence-and-safety lens: separating what is well established (e.g. post-meal walking lowers glucose; Baduanjin improves balance), what is plausible and what is traditional metaphor — and knowing when symptoms need a doctor, especially with diabetes, heart disease, pregnancy or medication.", ["evidence_quality", "dual_lens_translation", "five_phase_integration_matrix"]),
    },
    A={
        "daily_meta_health_protocol": ("The daily 元健康 Meta-Health protocol (日常元健康方案 — 'meta' as in 元, the whole above the parts: movement, eating, mind and rhythm as one practice; not 代谢/metabolic health) — a 24-hour blueprint: morning light and Baduanjin; pre-meal breaths, mindful meals to 70–80% full, gentle movement 30–40 minutes after eating; stress-release through the day; an early, light dinner; sleep before 子时 — personalized, observed and adjusted over time.", ["mind_body_digestive_loop", "five_phase_integration_matrix", "habit_formation", "personalization", "self_observation_feedback", "evidence_and_safety_lens"]),
    },
))


def build(ch):
    prereq = {n: [] for n in ch["P"]}
    for sec in ("C", "A"):
        for n, (_, pre) in ch[sec].items():
            assert n not in prereq, f"{ch['id']}: duplicate {n}"
            prereq[n] = pre
    for n, pre in prereq.items():
        for p in pre:
            assert p in prereq, f"{ch['id']}: {n} needs undefined {p}"
    tier = {}

    def t(n, stack=()):
        assert n not in stack, f"cycle at {n}"
        if n not in tier:
            tier[n] = 0 if not prereq[n] else 1 + max(t(p, stack + (n,)) for p in prereq[n])
        return tier[n]

    for n in prereq:
        t(n)
    used = {p for pre in prereq.values() for p in pre}
    orphans = [n for n in ch["P"] if n not in used]
    assert not orphans, f"{ch['id']}: unused primitives {orphans}"
    anc, todo = set(), [ch["capstone"]]
    while todo:
        for p in prereq[todo.pop()]:
            if p not in anc:
                anc.add(p); todo.append(p)
    dangling = [n for n in prereq if n not in anc and n != ch["capstone"]]
    assert not dangling, f"{ch['id']}: not on capstone path {dangling}"
    assert ch["capstone"] in ch["A"]

    missing = [n for n in prereq if n not in LABELS]
    assert not missing, f"{ch['id']}: no labels in locales/content.yaml for {missing}"
    order = lambda d: sorted(d, key=lambda n: (tier[n], n))
    out = {"domain": ch["id"], "primitives": {}, "concepts": {}, "applications": {}}
    for n in order(ch["P"]):
        out["primitives"][n] = {"defines": Folded(ch["P"][n]), "labels": LABELS[n], "tier": 0}
    for n in order(ch["C"]):
        d, pre = ch["C"][n]
        out["concepts"][n] = {"defines": Folded(d), "labels": LABELS[n], "composed_of": pre, "tier": tier[n]}
    for n in order(ch["A"]):
        d, pre = ch["A"][n]
        out["applications"][n] = {"defines": Folded(d), "labels": LABELS[n], "needs": pre, "tier": tier[n]}
    n_edges = sum(len(p) for p in prereq.values())
    return out, len(prereq), n_edges


# Keep generation results already registered in catalog.json: only the
# graph-derived fields are rewritten.
_prev = {}
if (ROOT / "catalog.json").exists():
    _prev = {e["id"]: e for e in json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))}

catalog = []
for ch in CH:
    out, n_nodes, n_edges = build(ch)
    d = ROOT / ch["id"] / "input"
    d.mkdir(parents=True, exist_ok=True)
    (d / "graph.yaml").write_text(
        yaml.dump(out, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
    text = DOMAINS[ch["id"]]
    # name/description are the source-language fallback; other languages go
    # under i18n.<lang> (read by src/data/catalog.js catalogText()).
    i18n = {}
    for field in ("name", "description"):
        for lang, val in text[field].items():
            if lang != SOURCE_LANG:
                i18n.setdefault(lang, {})[field] = val
    catalog.append({
        "id": ch["id"], "name": text["name"][SOURCE_LANG], "description": text["description"][SOURCE_LANG],
        "i18n": i18n,
        "capstone": ch["capstone"], "nodes": n_nodes, "edges": n_edges,
        "primitives": len(ch["P"]), "concepts": len(ch["C"]), "applications": len(ch["A"]),
        "tags": ["health", ch["tag"]], "has_navigator": True, "has_book": False,
        "books": [], "generated_concepts": [], "default_level": "core",
    })
    # Generation state (has_book, books, generated_concepts, pdfs, …) comes
    # from the previous catalog; graph-derived fields are always recomputed.
    graph_fields = {"id", "name", "description", "i18n", "capstone", "nodes", "edges",
                    "primitives", "concepts", "applications", "tags",
                    "has_navigator", "default_level"}
    for k, v in _prev.get(ch["id"], {}).items():
        if k not in graph_fields:
            catalog[-1][k] = v
    print(f"{ch['id']}: {n_nodes} nodes ({len(ch['P'])}P/{len(ch['C'])}C/{len(ch['A'])}A), {n_edges} edges, max tier {max(v['tier'] for v in out['applications'].values())}")

(ROOT / "catalog.json").write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
