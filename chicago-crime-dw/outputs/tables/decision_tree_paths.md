# Decision Tree Interpretation: Verbalized Decision Paths

The trained Decision Tree classifier isolates three dominant evidentiary paths determining arrest likelihood:

### Decision Path 1: Proactive Narcotics Enforcement (High Arrest Probability)
- **Path Logic:** `[PrimaryType_NARCOTICS > 0.5]`
- **Node Evaluation:** If the incident is classified as a Narcotics offense, the tree immediately routes to a leaf node predicting **Arrest Made = 1** with **>96% posterior arrest probability**.
- **Contextual Interpretation:** Narcotics violations in Chicago are predominantly proactive, officer-initiated operations (e.g. observation of street-level drug sales or contraband recovery during investigatory stops). Because detection occurs simultaneously with police apprehension, the arrest rate is nearly deterministic.

### Decision Path 2: Proactive Weapons & Concealed Carry Violations (High Arrest Probability)
- **Path Logic:** `[PrimaryType_NARCOTICS <= 0.5] -> [PrimaryType_WEAPONS VIOLATION > 0.5]`
- **Node Evaluation:** When the incident is not narcotics-related, the model evaluates whether a weapons offense occurred. If true, the tree predicts **Arrest Made = 1** with **~78% arrest probability**.
- **Contextual Interpretation:** Unlawful firearm possession and concealed carry violations are discovered upon physical pat-downs, vehicle searches, or direct officer intervention, creating strong statutory grounds for immediate custodial booking.

### Decision Path 3: Property Theft and Motor Vehicle Theft (Very Low Arrest Probability)
- **Path Logic:** `[PrimaryType_NARCOTICS <= 0.5] -> [PrimaryType_WEAPONS VIOLATION <= 0.5] -> [PrimaryType_MOTOR VEHICLE THEFT > 0.5 or LocationGroup_Street & Outdoor > 0.5]`
- **Node Evaluation:** For reported property crimes occurring outdoors or in transit without immediate police presence, the tree routes to a leaf node predicting **No Arrest = 0** with **<5% arrest probability**.
- **Contextual Interpretation:** These offenses are reported retrospectively by victims hours after the perpetrator has fled the scene. Without immediate suspect identification, physical evidence, or active tracking, on-scene arrest clearance is statistically negligible.
