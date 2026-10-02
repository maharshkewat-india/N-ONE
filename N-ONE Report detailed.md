## **CHAPTER 1 – INTRODUCTION** 

### **1.1 Background** 

Modern surveillance environments generate a large amount of visual information through cameras, recorded videos, webcams, and network-connected video sources. In a typical monitoring environment, an operator may have to observe multiple video feeds, identify relevant persons, recognize authorized personnel, investigate unknown individuals, and respond to potentially suspicious visual events. When these activities are performed entirely through manual observation, the process can become time-consuming, repetitive, and difficult to document consistently. 

The problem becomes more significant when the same person appears repeatedly at different times or camera locations. An operator may need to remember previous observations, compare the person's appearance with registered profiles, determine whether the person is an authorized Staff member or a Victim being searched for, and maintain an accurate record of when and where the observation occurred. Performing these activities manually can introduce inconsistencies and may make later review difficult. 

Artificial Intelligence (AI) and Computer Vision can assist with these tasks by providing automated or semi-automated analysis of visual information. Instead of requiring the operator to manually inspect every frame, a computer-vision system can identify faces, generate representations, compare them with registered profiles, maintain information about previously observed unknown individuals, and provide structured results to the operator. 

However, an AI-based surveillance system should not be considered a replacement for human judgment. Face recognition is affected by factors such as image quality, lighting, pose, occlusion, camera angle, enrollment quality, model configuration, and threshold selection. Similarly, visual threat detection can produce false positives or false negatives. Therefore, the role of N-ONE is designed as **AI-assisted surveillance** , where the system provides structured visual-analysis results while a human operator remains responsible for contextual interpretation, confirmation, and appropriate action. 

N-ONE— **No One Escapes** —is developed as an integrated dashboard that brings several surveillance-related capabilities into a single workflow. These capabilities include profile registration, Staff Recognition, target-restricted Victim Search, unknown-person re-identification, threat detection, camera-location recording, and structured CSV-based logging. 

The project is particularly focused on maintaining a clear distinction between an algorithmic result and a confirmed real-world identity. A recognition result represents the output of the configured recognition pipeline under the tested conditions; it is not an absolute guarantee of identity. 

### **1.2 AI Surveillance and Computer Vision** 

Computer Vision is a field of Artificial Intelligence concerned with enabling computer systems to process and interpret visual information. A typical computer-vision workflow consists of several stages, including image acquisition, preprocessing, detection, feature or representation extraction, comparison or classification, and presentation of the resulting information. 

N-ONE follows a similar processing structure. 

A simplified workflow can be represented as: 

**Camera/Video Input → Frame Acquisition → Detection → Branch-Specific Analysis → Decision/Status → Logging → Operator Review** 

The exact processing branch depends on the operational mode selected by the operator. 

For face-oriented operations, the system processes the incoming visual information to detect faces and perform recognition-related analysis. The detected face can then be compared with the relevant enrolled profile or profiles. 

For the Victim Search workflow, the system follows a more restricted process: 

**Camera Input → Face Detection → Selected Victim Comparison → Threshold Evaluation → Victim Result → Location/Time Logging** 

The threat-detection workflow is separate from the face-recognition workflow. It uses its own implemented threat-analysis logic rather than treating face-recognition model settings as threatdetection settings. 

This separation is important because face recognition and threat detection solve different computational problems. A face-recognition model attempts to determine whether a detected face corresponds to an enrolled identity, while threat detection attempts to identify visual characteristics associated with the implemented threat heuristic. 

Although the project is deployed as a Streamlit-based application, its functional architecture is divided into logical components. These components handle authentication, profile management, recognition, unknown-person storage, threat analysis, logging, and dashboard presentation. 

### **1.3 Face Recognition Context** 

Face detection and face recognition are related but different tasks. 

#### **Face Detection** 

Face detection attempts to answer: 

##### **Where is a face located in the image?** 

The output is generally a detected region or bounding box around a face. 

#### **Face Representation** 

After a face is detected, the system can generate a numerical representation of the facial characteristics. In deep-learning-based systems, this representation is commonly generated by a pretrained neural network. 

#### **Face Comparison** 

The representation obtained from the current frame can then be compared with a representation associated with an enrolled profile. 

The comparison produces a similarity or distance value depending on the configured recognition system and metric. 

#### **Threshold-Based Decision** 

The resulting distance is evaluated against a configured threshold. 

Conceptually: 

##### **Distance ≤ Threshold → Candidate Match** 

##### **Distance > Threshold → Not Accepted as Match** 

The exact behavior depends on the implementation and configured recognition backend. 

This threshold is important because a very restrictive threshold can reject genuine observations, while a less restrictive threshold can increase the possibility of accepting an incorrect match. Therefore, threshold selection should be based on evaluation evidence rather than an arbitrary value. 

### **1.4 Recognition Architecture in N-ONE** 

N-ONE supports two conceptually different face-processing routes. 

#### **1.4.1 Deep Learning Recognition Route** 

When the required DeepFace/TensorFlow environment is available, N-ONE can use the configured pretrained recognition-model interface. 

The evaluation environment has been used to examine models including: 

- FaceNet 

- FaceNet512 

- ArcFace 

These models are evaluated using a defined recognition metric and threshold. 

The benchmark environment and production application configuration are intentionally treated separately. A model performing well during an experimental benchmark is not automatically substituted into the live application. 

#### **1.4.2 OpenCV Fallback Route** 

When the required deep-learning environment is unavailable, N-ONE provides an OpenCV-based fallback route. 

The fallback implementation uses OpenCV-based face detection and image-processing techniques, including Haar-based detection and HOG/CLAHE-related processing. 

This route provides operational flexibility during environments where the full TensorFlow/DeepFace stack cannot be loaded. 

However, the fallback implementation should not be assumed to have the same recognition characteristics as the deep-learning models. For this reason, the report distinguishes the **production fallback capability** from the **experimental deep-learning benchmark** . 

### **1.5 Victim Identification Problem** 

The Victim Search problem in N-ONE is designed as a **one-target verification workflow** . 

In a conventional recognition scenario, a detected face could potentially be compared with multiple registered identities. Such behavior is not appropriate for every investigation because the operator may be specifically searching for one selected Victim. 

N-ONE therefore introduces a target-restricted search process. 

The operator first selects the Victim profile that is being searched for. The operator then provides or selects the relevant camera location and starts the Victim Search process. 

The system restricts the visible known-match search to the selected Victim profile. 

Conceptually: 

##### **Selected Victim → Incoming Frame → Detected Face → Target Comparison → Threshold Decision** 

If the target is matched under the configured recognition conditions, N-ONE can present a **VICTIM FOUND** result containing available information such as: 

- Victim name 

- Profile information 

- Recognition distance 

- Timestamp 

- Camera location 

- Active model/backend information 

- Available sighting history 

This design provides an important distinction between: 

##### **“The system found the selected Victim”** 

and 

##### **“The system recognized some registered person.”** 

The latter is not sufficient for the target-specific search workflow. 

Other observed faces may still be handled through the unknown-person mechanism, but they should not be displayed as the selected Victim merely because they resemble another registered profile. 

### **1.6 Need for N-ONE** 

The development of N-ONE is motivated by several practical and technical requirements. 

#### **1.6.1 Need for a Unified Dashboard** 

Multiple surveillance functions can become difficult to manage when they are distributed across separate applications. N-ONE provides a common Streamlit interface through which different operational modes can be accessed. 

The dashboard can bring together: 

- Authentication 

- Profile registration 

- Face recognition 

- Victim Search 

- Staff Recognition 

- Unknown-person handling 

- Threat detection 

- Logs 

- Inventory 

- Model configuration 

This provides a consistent user interface for the project. 

#### **1.6.2 Need for Controlled Enrollment** 

Recognition quality depends partly on the quality of enrolled reference images. Arbitrary images can introduce multiple faces, poor framing, unsuitable crops, or irrelevant background information. 

N-ONE therefore uses a controlled registration process. 

The registration process requires the expected visible face and saves a focused face crop. This creates a more consistent representation of enrolled subjects. 

#### **1.6.3 Need for Target-Specific Search** 

Searching for a missing or lost person is different from general face recognition. The operator generally has a specific target rather than a requirement to identify everyone visible in the camera. 

N-ONE addresses this through Victim-specific matching. 

#### **1.6.4 Need for Unknown-Person Context** 

Not every detected individual will correspond to a registered Staff or Victim profile. Treating every unmatched observation as an independent event can make repeated appearances difficult to understand. 

N-ONE maintains an unknown-person store and sighting information so that repeated observations can be associated with available unknown identities. 

#### **1.6.5 Need for Structured Evidence** 

A visual recognition result without a timestamp, location, or record of the event may be difficult to review later. 

N-ONE therefore maintains structured logs that can contain information associated with detection and recognition events. 

### **1.7 Project Overview** 

N-ONE is implemented as a Streamlit-based application that provides a dashboard for AI-assisted surveillance operations. 

At startup, the application prepares the required data structures and directories and initializes the Streamlit session state required for the current interaction. 

The application then presents an authentication gate. 

After successful authentication, the interface exposes functionality according to the authenticated role. 

#### **Administrator Workflow** 

The Administrator is responsible for management-related operations such as: 

1. Registering Staff profiles. 

2. Registering Victim profiles. 

3. Managing available model settings. 

4. Reviewing registered profiles. 

5. Managing relevant project data. 

6. Performing selected administrative reset operations. 

#### **Operator Workflow** 

The Operator is focused on operational activities such as: 

1. Selecting an operational mode. 

2. Selecting the required Victim target when performing Victim Search. 

3. Providing a camera/location value. 

4. Starting a camera, video, or other supported input source. 

5. Reviewing recognition or detection results. 

6. Inspecting unknown-person information. 

7. Reviewing available logs and inventory. 

The overall application flow can be summarized as: 

##### **Application Start** 

↓ 

##### **Directory and Data Initialization** 

↓ 

##### **Authentication** 

↓ 

##### **Role Identification** 

↓ 

##### **Dashboard** 

↓ 

##### **Operational Mode Selection** 

↓ 

##### **Video/Camera Input** 

↓ 

##### **Frame Processing** 

↓ 

##### **Recognition / Unknown Re-ID / Threat Analysis** 

↓ 

##### **Result Presentation** 

↓ 

##### **Location and Timestamp Logging** 

↓ 

**Operator Review** 

### **1.8 Operational Modes** 

N-ONE is designed around multiple operational use cases. 

#### **1.8.1 Lost Person Search** 

This mode is dedicated to searching for a selected Victim. 

The operator selects the target profile before beginning the search. The system then restricts visible known matching to that target. 

The result can include a dedicated **VICTIM FOUND** display when the target satisfies the configured matching criteria. 

#### **1.8.2 Member/Staff Attendance or Recognition** 

The Staff-oriented workflow can be used to recognize registered Staff members. 

This mode uses the available registered Staff profiles rather than restricting the search to a single Victim. 

The purpose is operational recognition rather than missing-person search. 

#### **1.8.3 Unknown Person Re-Identification** 

When a face cannot be matched to an appropriate registered identity, N-ONE can place the observation into the unknown-person workflow. 

The system can assign or maintain an unknown-person identifier and associate subsequent sightings with available information. 

This provides temporal context without automatically assigning an identity to an unknown individual. 

#### **1.8.4 Threat Detection** 

The threat-detection mode uses the implemented visual heuristic/contour-based logic to identify configured threat indicators. 

This branch operates independently from the face-recognition model selection. 

Consequently, changing the face-recognition model does not automatically change the threatdetection algorithm. 

### **1.9 Data and Evidence Flow** 

N-ONE uses several types of project data. 

#### **Profile Data** 

Registered Staff and Victim profiles provide reference information for recognition. 

#### **Unknown-Person Data** 

Unknown observations can be stored separately so that repeated observations can be associated with the same available unknown context. 

#### **Victim Sighting Data** 

Victim-specific detection records provide information about recognized target observations. 

#### **Audit Data** 

Structured logs provide a record of relevant system events. 

The overall evidence flow can therefore be represented as: 

##### **Input Image/Video** 

↓ 

##### **Detection** 

↓ 

##### **Recognition or Threat Analysis** 

↓ 

##### **Decision/Status** 

- ↓ 

##### **Evidence Record** 

↓ 

##### **Operator Review** 

This structure allows the visual result to be considered together with contextual information rather than as an isolated prediction. 

### **1.10 Location-Aware Monitoring** 

Camera location is an important contextual element of the N-ONE workflow. 

When the operator supplies a camera location, detection events can be associated with that location. 

For example, a Victim Search observation may contain: 

- Selected Victim 

- Detection timestamp 

- Camera location 

- Recognition distance 

- Active model/backend 

- Available previous sightings 

This provides more useful information for later investigation than storing only the identity result. 

The location information is supplied by the operational workflow and should therefore be interpreted as contextual metadata associated with the camera/source rather than as automatically verified physical geolocation. 

### **1.11 Audit and Logging** 

An important characteristic of N-ONE is its use of structured CSV-based logging. 

Different workflows maintain appropriate records, including unknown-person information and Victim sighting information. 

A structured log makes it possible to review: 

- What was detected 

- When it was detected 

- Where it was detected 

- Which workflow produced the result 

- Which recognition configuration was active where recorded 

- What recognition information was available 

This is particularly useful during project evaluation because experimental observations can be inspected after the live demonstration. 

The logs also provide a foundation for future migration to a more scalable database architecture. 

### **1.12 Human-in-the-Loop Operation** 

N-ONE is intentionally designed as an operator-assistance system. 

The recognition algorithm does not independently determine the real-world significance of an observation. The operator must consider the output together with visual evidence and operational context. 

For example, a system-generated Victim match should be treated as a detection requiring appropriate review rather than as unquestionable proof of identity. 

The human operator can: 

- Review the detected image. 

- Consider the camera context. 

- Examine previous sightings. 

- Confirm whether the observation is meaningful. 

- Escalate according to organizational procedures. 

- Handle possible false matches or missed detections. 

This human-in-the-loop design is especially important in surveillance systems because environmental conditions can affect automated recognition. 

### **1.13 Practical Importance of the Project** 

N-ONE combines several concepts that are often studied separately in academic projects. 

These include: 

- Artificial Intelligence 

- Computer Vision 

- Face Recognition 

- Image Processing 

- Role-Based Access Control 

- Data Logging 

- Re-identification 

- Threat Analysis 

- Model Evaluation 

● Security and Privacy 

The project therefore provides both a practical software implementation and an experimental environment for studying AI-assisted surveillance. 

From an academic perspective, the system can demonstrate how a computer-vision application moves from raw visual input to an operator-readable result. 

### **1.14 Research and Evaluation Perspective** 

A central principle of N-ONE is that a model should not be considered suitable merely because it produces visually convincing demonstrations. 

Recognition performance should be evaluated using a separate dataset and measurable metrics. 

The evaluation process can consider: 

- True Positive 

- True Negative 

- False Positive 

- False Negative 

- Precision 

- Recall 

- F1-score 

- False Acceptance Rate 

- False Rejection Rate 

- Recognition latency 

- Approximate processing throughput 

Different thresholds can also be tested. 

This is particularly important for Victim Search because the system must balance two different types of error: 

**False Acceptance:** An incorrect person is accepted as the selected Victim. 

**False Rejection:** The actual Victim is present but the system fails to accept the observation. 

A threshold that reduces one type of error can affect the other. Therefore, threshold selection should be supported by the project's evaluation evidence. 

### **1.15 Separation Between Experimental and Production Systems** 

N-ONE maintains a distinction between the benchmark environment and the live application. 

The benchmark environment can be used to evaluate different models and configurations under controlled conditions. 

The production application retains its configured operational backend unless a deliberate engineering decision is made to change it. 

This distinction is important because: 

##### **A benchmark result is evidence about the tested dataset and conditions; it is not automatically a production guarantee.** 

For example, an experimental model may demonstrate a particular behavior on the evaluation dataset while behaving differently under different lighting, camera angles, image resolutions, or population characteristics. 

Therefore, N-ONE treats experimental model selection as an evidence-based engineering process. 

### **1.16 Project Limitations** 

Although N-ONE provides several useful capabilities, its operation is subject to technical limitations. 

Recognition performance can be affected by: 

- Lighting conditions 

- Face angle 

- Occlusion 

- Motion blur 

- Camera quality 

- Distance from the camera 

- Enrollment-image quality 

- Recognition threshold 

- Available computational resources 

- Dataset size and diversity 

Unknown-person re-identification can also be affected by changes in appearance, viewpoint, image quality, and available observations. 

Threat detection based on visual heuristics can produce both false positives and false negatives. 

The system therefore should not be presented as providing guaranteed identity recognition, guaranteed threat detection, or universal real-world performance. 

### **1.17 Ethical and Privacy Considerations** 

Face recognition and surveillance involve sensitive privacy considerations. 

N-ONE attempts to provide technical controls such as: 

- Role separation 

- Controlled registration 

- Target-restricted Victim Search 

- Structured logging 

- Explicit operator involvement 

- Separation of experimental and production environments 

However, technical controls alone do not establish legal compliance. 

A real-world deployment would require appropriate consideration of: 

- Applicable law 

- Organizational policy 

- Data retention 

- Access control 

- Consent or other lawful basis where applicable 

- Data security 

- Purpose limitation 

- Responsible handling of biometric information 

- Human review procedures 

The project is therefore best understood as an academic and experimental platform unless the necessary deployment governance is separately established. 

### **1.18 Significance of N-ONE** 

The main significance of N-ONE is the integration of multiple computer-vision and surveillance functions into a single controlled workflow. 

Instead of treating face recognition, unknown-person tracking, threat analysis, logging, and operator interaction as unrelated components, N-ONE combines them into a common architecture. 

Its workflow can be summarized as: 

##### **Register → Monitor → Detect → Compare → Contextualize → Log → Review** 

This approach makes the project useful not only as a software prototype but also as an environment for evaluating the practical behavior and limitations of AI-assisted surveillance. 

### **1.19 Summary** 

N-ONE is an AI-assisted surveillance platform developed to combine several computer-vision operations within a single operator-oriented dashboard. The system supports controlled Staff and Victim registration, target-restricted Victim Search, Staff recognition, unknown-person reidentification, threat analysis, location-aware monitoring, and structured logging. 

The project distinguishes between face detection, face representation, face comparison, and threshold-based recognition decisions. It also distinguishes between the deep-learning recognition route and the OpenCV fallback route. 

A major design principle is the separation of **experimental benchmark evidence from production behavior** . This allows different recognition models and thresholds to be evaluated without silently changing the live application. 

The system is intended to assist human operators rather than replace them. Recognition and threat results should therefore be interpreted in context, reviewed by an authorized operator, and treated according to the limitations of the underlying data, algorithms, and operating environment. 

Thus, N-ONE provides a practical foundation for studying the integration of **Computer Vision, Artificial Intelligence, Face Recognition, Re-identification, Threat Analysis, Security Controls, Logging, and Model Evaluation** within an academic software project. 

# **CHAPTER 2 – OBJECTIVES OF THE PROJECT** 

### **2.1 Primary Objective** 

The primary objective of **N-ONE (No One Escapes)** is to develop an integrated, authenticated, and operator-oriented AI-assisted surveillance dashboard capable of supporting **face-based Victim Search, registered-person recognition, unknown-person re-identification, and heuristic threat monitoring** through local, uploaded, recorded, or browser-based video sources. 

The project is intended to provide a single environment in which an authorized user can register subjects, select an operational mode, process visual input, obtain recognition or threat-analysis results, and review associated records. 

The system is not intended to replace a trained human operator or provide absolute identity verification. Instead, its primary objective is to provide **consistent computational assistance, contextual information, and reviewable evidence** that can support an operator during surveillance and investigation workflows. 

The primary objective can therefore be summarized as: 

**To design and implement a modular AI-assisted surveillance platform that combines controlled subject enrollment, target-restricted face recognition, unknown-person tracking, threat-oriented visual analysis, location-aware logging, and experimental model evaluation within a secure operator dashboard.** 

The objective is further divided into functional, technical, security, evaluation, usability, and research-oriented objectives. 

## **2.2 Functional Objectives** 

### **2.2.1 Implement Role-Based Authentication** 

The first functional objective is to provide an authentication mechanism that distinguishes between different types of users. 

N-ONE defines two operational roles: 

- **Administrator** 

##### ● **Operator** 

The Administrator is responsible for management and configuration activities, while the Operator is primarily responsible for surveillance and monitoring operations. 

The objective is to ensure that sensitive administrative functionality is not exposed as part of the normal Operator workflow. 

### **2.2.2 Provide Administrator and Operator Workflows** 

The system should provide different capabilities according to the authenticated role. 

#### **Administrator capabilities include:** 

- Registering Staff profiles. 

- Registering Victim profiles. 

- Managing model configuration. 

- Reviewing registered profile inventory. 

- Performing selected administrative data-management operations. 

#### **Operator capabilities include:** 

- Selecting operational modes. 

- Monitoring video sources. 

- Selecting a Victim for target-specific search. 

- Entering camera/location information. 

- Reviewing recognition results. 

- Reviewing unknown-person observations. 

- Inspecting available logs and inventory information. 

This separation provides a clear operational boundary between system administration and routine surveillance. 

### **2.2.3 Register Staff and Victim Profiles** 

The system should provide a controlled mechanism for registering two major categories of subjects: 

1. **Staff** 

2. **Victim** 

The registration workflow should allow an Administrator to provide an image either through an uploaded file or through a supported camera-capture mechanism. 

The profile should then be processed and stored using a predictable identifier. 

For example, the implemented naming convention distinguishes the subject categories through identifiers such as: 

- Staff_<name>.jpg 

- Victim_<name>.jpg 

This provides a consistent structure for later profile retrieval and recognition. 

### **2.2.4 Enforce Single-Face Enrollment** 

A major functional objective is to prevent unsuitable registration images from being accepted. 

During profile enrollment, the system should require **exactly one detectable face** . 

The purpose of this requirement is to prevent ambiguity during enrollment. 

If an image contains: 

- No detectable face, or 

- More than one detectable face, 

the image should not be accepted as a valid single-subject enrollment image. 

This helps maintain consistency between the intended identity and the stored facial reference. 

### **2.2.5 Store Focused Face Crops** 

After successful enrollment, N-ONE should save a padded crop centered around the detected face instead of unnecessarily storing the complete original registration image as the recognition reference. 

The padding provides some surrounding facial context while maintaining focus on the subject. 

The objective is to make enrolled references more consistent for subsequent face-processing operations. 

The workflow can be represented as: 

**Input Image → Face Detection → Validation → Face Bounding Box → Padding → Face Crop → Profile Storage** 

## **2.3 Victim Search Objectives** 

### **2.3.1 Implement Target-Restricted Victim Search** 

One of the most important objectives of N-ONE is to provide a dedicated **Victim Search** mode. 

The operator should select a specific registered Victim before beginning the search. 

The recognition process should then restrict visible known matching to that selected target. 

The intended workflow is: 

**Select Victim → Select/Enter Camera Location → Start Video → Detect Face → Compare With Selected Victim → Evaluate Threshold → Display Result** 

This prevents the Victim Search interface from behaving like an unrestricted identity search. 

### **2.3.2 Prevent Unrelated Registered Profiles From Appearing as the Target** 

The Victim Search objective includes maintaining a strict distinction between the selected Victim and unrelated registered individuals. 

For example, if the selected target is: 

##### **Victim A** 

and the camera contains: 

##### **Staff B** 

the system should not display Staff B as the selected Victim merely because a face was detected. 

This target restriction is an important part of the intended search logic. 

### **2.3.3 Provide Victim Detection Context** 

When the selected Victim satisfies the configured recognition conditions, the system should provide contextual information rather than only displaying a generic match message. 

The Victim Search result can include: 

- Victim name 

- Profile identifier 

- Recognition distance 

- Timestamp 

- Camera location 

- Active model/backend 

- Recognition metric 

- Available sighting history 

The objective is to make the result reviewable and context-aware. 

### **2.3.4 Maintain Victim Sighting History** 

N-ONE should record Victim observations in a structured sighting log. 

This allows an operator to review available previous observations instead of treating each detection as an isolated event. 

The objective is to provide information such as: 

##### **Who → Where → When → Recognition Information** 

This can be useful during subsequent review of the monitoring process. 

## **2.4 Registered-Person Recognition Objectives** 

### **2.4.1 Support Staff Recognition** 

In addition to target-specific Victim Search, N-ONE should support recognition of registered Staff members during attendance-style or general recognition operation. 

Unlike Victim Search, this workflow can compare detected faces against the appropriate registered Staff profiles. 

The objective is to demonstrate how the same recognition infrastructure can support a different operational use case. 

### **2.4.2 Support Configurable Recognition** 

The system should provide configurable recognition parameters where supported by the implementation. 

These include: 

- Recognition model 

- Face detector 

- Distance/similarity metric 

- Recognition threshold 

This provides flexibility for experimentation and operational calibration. 

## **2.5 Unknown-Person Tracking Objectives** 

### **2.5.1 Register Unknown Observations** 

Not every detected face will correspond to a registered Staff or Victim. 

Therefore, an important objective is to maintain information about unmatched individuals instead of simply discarding every unmatched observation. 

The system should be able to store relevant unknown-person information locally. 

### **2.5.2 Support Unknown Re-Identification** 

The project aims to associate repeated observations with an existing unknown-person identity when the available recognition mechanism indicates sufficient similarity. 

The intended conceptual workflow is: 

**Unknown Face → Generate Representation → Compare With Unknown Cache → Existing Unknown / New Unknown → Store Sighting** 

This provides continuity between repeated observations. 

### **2.5.3 Preserve Unknown-Person Context** 

The objective is not to assign a real-world identity to an unknown person without evidence. 

Instead, the system should maintain a local identifier such as an unknown-person ID and use it to group observations. 

Therefore: 

**Unknown Re-ID provides continuity of observations, not verified real-world identity.** 

This distinction is important for responsible interpretation of the results. 

## **2.6 Threat Detection Objectives** 

### **2.6.1 Detect Possible Threat Indicators** 

N-ONE includes a separate threat-analysis workflow intended to identify visual patterns associated with configured threat indicators. 

The current implementation includes heuristic/contour-oriented analysis for possible: 

- Elongated weapon-like regions 

- Warm fire-like regions 

The objective is to provide an additional visual monitoring signal for the operator. 

### **2.6.2 Separate Threat Detection From Face Recognition** 

Threat detection and face recognition solve different problems. 

Therefore, a specific objective is to keep their configuration and processing logic conceptually separate. 

Changing the face-recognition model should not automatically change the threat-detection logic. 

This modularity allows each subsystem to be tested independently. 

### **2.6.3 Provide Operator-Readable Threat Status** 

The threat-processing branch should provide a status that can be displayed through the dashboard. 

The objective is to make the result understandable to the operator rather than exposing only lowlevel image-processing information. 

The result should be interpreted as a **possible threat indicator** , not as a guaranteed classification of an object or event. 

## **2.7 Technical Objectives** 

### **2.7.1 Use a Modular Computer-Vision Architecture** 

The technical objective is to organize the system into logical processing components rather than implementing every operation as a single monolithic workflow. 

Major functional areas include: 

- Authentication 

- Profile registration 

- Face detection 

- Face recognition 

- Victim Search 

- Unknown-person processing 

- Threat analysis 

- Logging 

- Dashboard presentation 

This modular structure makes the application easier to understand, test, and extend. 

### **2.7.2 Use the Selected Technology Stack** 

The project is implemented using technologies including: 

- **Python** 

- **Streamlit** 

- **OpenCV** 

- **NumPy** 

- **Pandas** 

- **Pillow** 

- **DeepFace-compatible recognition components** 

Each technology serves a particular role within the application. 

#### **Python** 

Provides the primary programming environment. 

#### **Streamlit** 

Provides the interactive dashboard and operator interface. 

#### **OpenCV** 

Supports image and video processing, face detection, and computer-vision operations. 

#### **NumPy** 

Supports numerical image and feature-processing operations. 

#### **Pandas** 

Supports structured tabular data and CSV-based logging. 

#### **Pillow** 

Supports image loading and manipulation where required. 

#### **DeepFace-compatible components** 

Provide access to pretrained face-recognition model interfaces when the required environment is available. 

## **2.8 Model Configuration Objectives** 

The project provides an Administrator-side configuration mechanism for relevant face-recognition parameters. 

The technical objective is to allow controlled configuration of: 

#### **Recognition Model** 

The project can work with configured recognition models such as: 

- FaceNet 

- FaceNet512 

- ArcFace 

depending on the environment and evaluation workflow. 

#### **Detector** 

The face-detection component can be configured according to the supported backend. 

#### **Distance Metric** 

The recognition pipeline can use the configured metric, such as cosine distance. 

#### **Threshold** 

The threshold determines the acceptance boundary for a recognition comparison. 

The objective is to make these parameters explicit rather than hiding them inside an unobservable processing pipeline. 

## **2.9 Image Processing Objectives** 

The project should process visual input efficiently enough for its intended local demonstration and evaluation environment. 

For the main OpenCV path, the processing width is capped at approximately **1280 pixels** . 

The objective of this restriction is to avoid unnecessary computational overhead caused by processing very high-resolution frames when such resolution does not provide proportional benefit for the implemented workflow. 

The system also maintains in-memory caches for known and unknown face information where appropriate. 

This reduces repeated loading and comparison operations during ongoing processing. 

## **2.10 Video Input Objectives** 

N-ONE should support practical visual-input mechanisms appropriate to the implemented application. 

The project can work with sources such as: 

- Browser camera/WebRTC 

- Local webcam 

- Pre-recorded video 

- Supported IP/RTSP sources 

The objective is to allow the same recognition and threat-analysis workflows to operate on different forms of visual input without requiring a completely different application interface. 

## **2.11 Data Management Objectives** 

### **2.11.1 Predictable Data Paths** 

The system should maintain predictable local locations for: 

- Registered profiles 

- Unknown-person information 

- Victim sightings 

- Audit records 

- Evaluation datasets 

- Evaluation results 

This makes the project easier to inspect and reproduce. 

### **2.11.2 Structured CSV Logging** 

The system should store relevant records in structured CSV files. 

Examples include: 

- unknown_person_db.csv 

- unknown_sighting_log.csv 

- victim_sighting_log.csv 

The objective is to provide simple, inspectable, and portable records during the academic development and evaluation stages. 

### **2.11.3 Preserve Reviewable Evidence** 

Important system events should retain enough contextual information to support later inspection. 

Depending on the workflow, this may include: 

- Identity/profile 

- Timestamp 

- Location 

- Distance 

- Model/backend 

- Detection status 

- Sighting information 

This supports the project's evidence-oriented approach. 

## **2.12 Security Objectives** 

Security is an important component of N-ONE because the application contains registered identity information and surveillance-related records. 

### **2.12.1 Protect Authentication Secrets** 

The application uses configured secret values for authentication. 

The objective is to prevent the system from operating in an authenticated mode when the required secret configuration is absent. 

The system therefore remains locked when the required authentication secrets have not been properly configured. 

### **2.12.2 Use Constant-Time Credential Comparison** 

The authentication workflow uses constant-time comparison for submitted credentials. 

The objective is to reduce the potential for timing-based information leakage during credential comparison. 

This is a specific implementation-level security control and should not be interpreted as providing complete authentication security by itself. 

### **2.12.3 Temporary Lockout** 

The application applies a temporary lockout after repeated failed authentication attempts. 

The objective is to make repeated automated or accidental credential attempts less effective. 

This provides an additional protection layer around the dashboard authentication process. 

### **2.12.4 Enforce Role Separation** 

Administrator-only controls should remain unavailable to ordinary Operators. 

This includes sensitive operations such as: 

- Profile registration 

- Model configuration 

- Administrative data management 

The objective is to reduce unnecessary access to management functionality. 

### **2.12.5 Recognize Security Limitations** 

The implemented authentication controls should not be described as a complete enterprise identitymanagement system. 

The project does not automatically establish: 

- Enterprise SSO 

- Multi-factor authentication 

- Centralized identity management 

- Comprehensive session management 

- Full database-level access control 

- Complete biometric-data governance 

Therefore, the security objective is to provide **basic application-level access separation appropriate to the current prototype** , while documenting the requirements for future hardening. 

## **2.13 Evaluation Objectives** 

### **2.13.1 Establish a Separate Evaluation Workspace** 

A dedicated evaluation workspace is used to keep experimental evidence separate from the live application. 

The objective is to prevent benchmark experimentation from silently modifying the production configuration. 

### **2.13.2 Separate Enrollment and Test Data** 

The evaluation dataset should maintain separate enrollment and test paths. 

This is important because evaluating a model using the exact same image used for enrollment can produce misleadingly optimistic results. 

The objective is therefore to test the recognition system using images that are separate from the enrollment references. 

### **2.13.3 Validate Dataset Structure** 

The evaluation system should verify that: 

- Required directories exist. 

- Expected metadata fields are available. 

- Referenced files exist. 

- Enrollment and test data are appropriately separated. 

- Dataset information is recorded consistently. 

This makes the benchmark more reproducible. 

### **2.13.4 Compare Multiple Recognition Models** 

The evaluation objective includes comparing multiple recognition models rather than assuming that one model is automatically suitable. 

The benchmark environment can evaluate: 

- FaceNet 

- FaceNet512 

- ArcFace 

under the defined evaluation conditions. 

The results should be treated as evidence for the tested dataset and configuration. 

### **2.13.5 Evaluate Multiple Thresholds** 

The evaluation should examine recognition behavior at multiple threshold values. 

The purpose is to determine how the acceptance boundary affects: 

- Genuine Victim acceptance 

- Incorrect acceptance 

- False rejection 

- False acceptance 

This provides a more complete view of recognition behavior than evaluating only one threshold. 

### **2.13.6 Calculate Recognition Metrics** 

The evaluation workspace should calculate standard classification metrics, including: 

#### **True Positive (TP)** 

The selected Victim is present and correctly accepted. 

#### **True Negative (TN)** 

The selected Victim is absent and correctly rejected. 

#### **False Positive (FP)** 

A non-target person is incorrectly accepted as the selected Victim. 

#### **False Negative (FN)** 

The genuine Victim is present but is incorrectly rejected. 

From these values, the evaluation can calculate: 

##### **Precision** 

Precision=TPTP+FPPrecision = \frac{TP}{TP+FP} 

##### **Recall** 

Recall=TPTP+FNRecall = \frac{TP}{TP+FN} 

##### **F1-Score** 

F1=2×Precision×RecallPrecision+RecallF1 = 2 \times \frac{Precision \times Recall}{Precision + Recall} 

##### **False Acceptance Rate** 

FAR=FPFP+TNFAR = \frac{FP}{FP+TN} 

##### **False Rejection Rate** 

FRR=FNFN+TPFRR = \frac{FN}{FN+TP} 

These metrics provide different perspectives on system behavior. 

## **2.14 Performance Evaluation Objectives** 

The project should not evaluate recognition only by correctness. 

It should also record computational performance where measurement is available. 

Important measurements include: 

- Average inference/processing latency 

- Approximate FPS 

- Model initialization time where relevant 

- CPU utilization where measured 

- GPU availability/use where measured 

- Memory requirements where measured 

The objective is to understand the practical computational cost of the recognition pipeline. 

However, benchmark FPS should not automatically be presented as the application's universal realtime FPS because actual performance depends on the complete pipeline, camera source, resolution, hardware, and processing configuration. 

## **2.15 Multi-Frame Evaluation Objective** 

An additional objective is to investigate whether requiring multiple consecutive frames before confirming a recognition result can improve operational reliability. 

Potential confirmation windows include: 

- 1 frame 

- 3 frames 

- 5 frames 

However, multi-frame performance should only be reported when suitable labeled video-sequence data exists. 

If sequence data is unavailable, the system should explicitly record the multi-frame evaluation as **not available** rather than generating artificial results. 

This maintains the integrity of the evaluation. 

## **2.16 Reproducibility Objectives** 

N-ONE should make its experimental process sufficiently transparent that the evaluation can be repeated. 

The objective is to document: 

- Dataset structure 

- Enrollment images 

- Test images 

- Model 

- Detector 

- Metric 

- Threshold 

- Evaluation conditions 

- Result metrics 

- Performance measurements 

- Limitations 

This allows future developers or evaluators to understand how a reported result was obtained. 

## **2.17 Documentation Objectives** 

A major project objective is to document not only what the system does but also how it works. 

The documentation should cover: 

- System architecture 

- Modules 

- Data flow 

- Authentication 

- Profile registration 

- Recognition workflow 

- Victim Search 

- Unknown Re-ID 

- Threat detection 

- Logging 

- Evaluation methodology 

- Testing 

- Security 

- Privacy 

- Limitations 

- Future scope 

The documentation should be based on the actual implementation rather than hypothetical features. 

## **2.18 Usability Objectives** 

N-ONE should provide an interface that allows an authorized operator to understand the current system state without requiring direct interaction with the underlying Python implementation. 

The dashboard should make important information visible, including: 

- Current authenticated role 

- Active operational mode 

- Selected Victim 

- Camera location 

- Recognition/detection status 

- Profile inventory 

- Available logs 

- Relevant images 

The objective is to make the system suitable for practical demonstration and controlled operational use. 

## **2.19 Research Objectives** 

From a research and academic perspective, N-ONE aims to provide an environment in which different AI-based recognition configurations can be experimentally compared. 

The research-oriented objectives include: 

1. Understanding the behavior of different recognition models. 

2. Studying threshold sensitivity. 

3. Measuring false acceptance and false rejection. 

4. Comparing computational latency. 

5. Studying the effect of enrollment/test separation. 

6. Documenting environmental limitations. 

7. Maintaining a clear distinction between benchmark evidence and production configuration. 

The project therefore emphasizes **measurement and traceability** rather than making unsupported claims about universal AI performance. 

## **2.20 Ethical Objectives** 

The project also has several responsible-use objectives. 

These include: 

- Maintaining human oversight. 

- Avoiding automatic claims of absolute identity. 

- Restricting Victim Search to the selected target. 

- Avoiding unsupported identification of unknown individuals. 

- Documenting system limitations. 

- Separating experimental evidence from production behavior. 

- Recognizing privacy implications of facial data. 

- Maintaining appropriate access restrictions. 

These objectives are intended to reduce inappropriate interpretation of automated results. 

They do not, by themselves, establish legal compliance for real-world surveillance deployment. 

## **2.21 Expected Outcomes** 

The expected outcome of N-ONE is a **demonstrable, locally reproducible AI-assisted surveillance prototype** that integrates multiple computer-vision workflows into one authenticated dashboard. 

The expected system should provide: 

#### **Authentication** 

A working Administrator/Operator access structure. 

#### **Profile Management** 

Controlled Staff and Victim enrollment with single-face validation and predictable profile storage. 

#### **Victim Search** 

A target-restricted workflow capable of producing a Victim result when the configured recognition conditions are satisfied. 

#### **Staff Recognition** 

Recognition of registered Staff profiles during the appropriate operational workflow. 

#### **Unknown Re-ID** 

Local storage and repeat-observation handling for unknown persons. 

#### **Threat Monitoring** 

Heuristic visual monitoring for the implemented threat indicators. 

#### **Logging** 

Structured local records containing available detection and sighting information. 

#### **Evaluation** 

A separate benchmark environment capable of comparing recognition configurations using measurable metrics. 

#### **Documentation** 

A source-backed technical explanation of the implementation, evaluation, security controls, limitations, and future scope. 

## **2.22 What the Project Does Not Claim** 

A critical objective of the project documentation is to maintain realistic boundaries around the system's capabilities. 

N-ONE does **not** claim: 

- Universal face-recognition accuracy. 

- Guaranteed Victim discovery. 

- Guaranteed real-time performance under all hardware conditions. 

- Guaranteed threat classification. 

- Perfect unknown-person re-identification. 

- Legal compliance merely because technical controls are present. 

- Automatic replacement of trained surveillance personnel. 

- That benchmark results represent all real-world populations or environments. 

These boundaries are important because an academic prototype should distinguish between **implemented capability** , **measured experimental evidence** , and **future potential** . 

## **2.23 Objective-to-Module Mapping** 

**Objective Primary N-ONE Component** 

Administrator authentication Authentication/RBAC 

|Operator authentication|Authentication/RBAC|
|---|---|
|Staff registration|Profile Registration|
|Victim registration|Profile Registration|
|Single-face enrollment|Face Validation|
|Face-crop storage|Profile Storage|
|Victim Search|Victim Search Engine|
|Staff recognition|Recognition Workflow|
|Unknown tracking|Unknown Person Store|
|Unknown re-identification|Unknown Matching|
|Victim sighting history|Victim Sighting Logger|
|Camera/location context|Monitoring Workflow|
|Threat monitoring|Threat Detection Module|
|Model configuration|Administrator Configuration|
|Recognition benchmarking|Evaluation Workspace|
|Threshold analysis|Evaluation Workspace|
|Audit records|CSV Logging|
|Operator review|Streamlit Dashboard|
|Security separation|Authentication/RBAC|



## **2.24 Summary of Project Objectives** 

The objectives of N-ONE can be summarized into six major categories: 

#### **1. Functional Objective** 

Develop a single dashboard capable of supporting Victim Search, Staff recognition, unknownperson re-identification, and threat monitoring. 

#### **2. Technical Objective** 

Integrate computer-vision and recognition technologies into a modular Python/Streamlit application with configurable recognition parameters. 

#### **3. Security Objective** 

Provide authenticated Administrator and Operator workflows, constant-time credential comparison, temporary failed-login lockout, and role-based access separation. 

#### **4. Evaluation Objective** 

Provide a separate, reproducible evaluation environment for comparing recognition models and thresholds using TP, TN, FP, FN, Precision, Recall, F1, FAR, and FRR. 

#### **5. Documentation Objective** 

Create source-backed documentation describing the architecture, implementation, testing, benchmark evidence, security controls, limitations, and future scope. 

#### **6. Responsible-Use Objective** 

Maintain human oversight and clearly distinguish automated recognition results from confirmed real-world identity or threat conclusions. 

### **2.25 Final Objective Statement** 

The overall objective of N-ONE is therefore: 

**To develop and evaluate an authenticated, modular, AI-assisted surveillance platform that can perform controlled subject enrollment, target-restricted Victim Search, registered-person recognition, unknown-person re-identification, and heuristic threat monitoring while maintaining structured location-aware records, measurable evaluation evidence, role-based access controls, and clearly documented technical, performance, privacy, and operational limitations.** 

The expected result is not a system that guarantees correct identification in every situation. Rather, the project aims to provide a **reproducible and evidence-oriented prototype** in which computervision algorithms assist authorized human operators and where system behavior can be measured, reviewed, and improved through controlled experimentation. 

## **CHAPTER 3 – SCOPE OF THE PROJECT** 

### **3.1 Introduction** 

The scope of a software project defines the functional, technical, operational, security, evaluation, and deployment boundaries within which the system is designed and assessed. Clearly defining scope is particularly important for an AI-assisted surveillance system because the capabilities demonstrated by a prototype should not be interpreted as capabilities that have not been implemented or experimentally validated. 

**N-ONE (No One Escapes)** is scoped as an integrated, locally deployable, AI-assisted surveillance and visual-analysis platform. Its current implementation combines authentication, subject registration, face-based recognition workflows, target-restricted Victim Search, unknown-person tracking, threat-oriented visual analysis, location-aware logging, and an experimental modelevaluation workspace. 

The scope is deliberately limited to the capabilities that are implemented and supported by the project evidence. Areas such as large-scale multi-camera orchestration, enterprise identity federation, encrypted biometric storage, comprehensive security-event infrastructure, and full production deployment are outside the current implementation. 

The scope can be divided into the following areas: 

1. Functional Scope 

2. Operational Scope 

3. AI and Computer-Vision Scope 

4. Video-Input Scope 

5. Data and Storage Scope 

6. Security Scope 

7. Evaluation and Dataset Scope 

8. User and Role Scope 

9. Deployment Scope 

10. Out-of-Scope Areas 

11. Scope Limitations 

12. Future Expansion Boundary 

## **3.2 Functional Scope** 

The functional scope describes the features that are implemented within the N-ONE application. 

The current implementation includes the following major functional areas: 

- Authentication 

- Role-based access 

- Profile registration 

- Staff and Victim classification 

- Profile inventory 

- Registered-photo viewing 

- Victim Search 

- Staff/registered-person recognition 

- Unknown-person tracking 

- Victim sighting history 

- Threat-oriented visual analysis 

- Camera/location information 

- CSV-based logging 

- Model configuration 

- Evaluation workspace 

These functions are integrated into a Streamlit-based dashboard. 

### **3.2.1 Authentication** 

The system includes an authentication gate that must be passed before the protected dashboard becomes available. 

The authentication scope includes: 

- Administrator login 

- Operator login 

- Secret-based credential configuration 

- Failed-attempt handling 

- Temporary lockout 

- Logout/session handling 

The purpose of authentication within the project is to establish a basic access boundary between authorized users and unauthenticated visitors. 

The current authentication mechanism is application-level authentication and should not be interpreted as an enterprise identity-management system. 

### **3.2.2 Role-Based Access** 

N-ONE defines two primary roles: 

#### **Administrator** 

The Administrator has access to management-oriented functionality. 

This includes: 

- Staff registration 

- Victim registration 

- Model configuration 

- Inventory management 

- Selected administrative data operations 

#### **Operator** 

The Operator is intended for routine monitoring and investigation workflows. 

This includes: 

- Video monitoring 

- Victim Search 

- Registered-person recognition 

- Unknown-person review 

- Log inspection 

- Operational dashboard functions 

The scope therefore includes basic role separation within the application. 

## **3.3 Profile Registration Scope** 

N-ONE includes a controlled profile-enrollment workflow for registered subjects. 

The two supported subject categories are: 

- **Staff** 

- **Victim** 

The Administrator can provide a source image through supported upload or capture mechanisms. 

The registration pipeline validates the image before creating the profile. 

### **3.3.1 Single-Face Enrollment** 

A major part of the registration scope is the requirement that the enrollment image contain exactly one detectable face. 

This prevents an image containing several people from being ambiguously associated with a single profile. 

The registration process therefore follows approximately: 

##### **Input Image → Face Detection → Face Count Validation → Crop → Storage** 

An image with zero or multiple detected faces is not considered a valid single-subject enrollment image. 

### **3.3.2 Face-Crop Storage** 

After successful validation, N-ONE stores a padded face crop. 

The purpose is to create a focused reference image for subsequent recognition operations. 

The scope therefore includes controlled face-reference creation rather than unrestricted storage of arbitrary registration images. 

### **3.3.3 Predictable Profile Identification** 

The system uses predictable local profile naming conventions. 

The implemented convention includes identifiers such as: 

- Staff_<name>.jpg 

- Victim_<name>.jpg 

Legacy naming conventions such as Member_ and Lost_ can also be interpreted according to the existing implementation. 

This predictable structure makes profile discovery and local inventory management easier. 

## **3.4 Inventory and Photo-Viewing Scope** 

The application provides an inventory-oriented interface for registered profiles. 

The inventory can distinguish between relevant categories such as: 

- All profiles 

- Staff 

- Victim 

The system also provides a read-oriented photo viewer for registered profile images. 

The scope of this functionality is primarily inspection and operational management. It is not intended to provide a full enterprise biometric database-management system. 

## **3.5 Operational Mode Scope** 

N-ONE currently provides multiple operational modes. 

The major operational modes are: 

1. **Lost Person Search / Victim Search** 

2. **Member/Staff Recognition or Attendance** 

3. **Threat Detection** 

Unknown-person handling is integrated into the recognition workflows and associated datamanagement functions. 

Each mode addresses a different operational requirement. 

### **3.5.1 Victim Search Scope** 

The Victim Search mode is designed around a selected Victim target. 

The operator selects one Victim and provides the relevant camera/location information. 

The system then restricts visible known matching to the selected target. 

The scope includes: 

- Victim selection 

- Target-specific face comparison 

- Recognition threshold evaluation 

- Victim-found result display 

- Timestamp recording 

- Camera-location recording 

- Sighting-history display 

The system does not claim that a positive algorithmic match constitutes absolute proof of identity. 

### **3.5.2 Staff Recognition Scope** 

The system also supports registered-person recognition for Staff-oriented operation. 

This allows a detected face to be compared with appropriate registered profiles. 

However, the current project scope does **not** establish a comprehensive Staff recognition accuracy benchmark equivalent to the dedicated Victim evaluation. 

Therefore, the capability is implemented, while a complete quantitative Staff recognition evaluation remains outside the established evidence. 

### **3.5.3 Unknown-Person Tracking Scope** 

When a detected person does not correspond to an appropriate registered identity, the system can maintain an unknown-person record. 

The scope includes: 

- Unknown-person storage 

- Local unknown IDs 

- Repeat observation handling 

- Unknown sighting information 

The purpose is to maintain continuity between observations. 

It does not establish the real-world identity of the person. 

### **3.5.4 Threat Detection Scope** 

The threat-detection branch is intended to identify visual patterns associated with the implemented threat heuristics. 

The current scope includes analysis related to: 

- Possible elongated weapon-like contours 

- Possible warm fire-like regions 

The system presents these as visual indicators for operator attention. 

The project does not establish a comprehensive benchmark proving the accuracy of these threat detections under all real-world conditions. 

## **3.6 Video-Input Scope** 

N-ONE is designed to work with several visual-input mechanisms supported by the implementation. 

These include: 

#### **Browser Camera** 

Browser-based camera/WebRTC input can be used for live monitoring. 

#### **Local Webcam** 

A locally connected camera can be accessed through the OpenCV-based processing path where supported. 

#### **Pre-Recorded Video** 

Video files can be used for controlled testing and demonstrations. 

#### **IP/RTSP Sources** 

IP-camera access can be represented by passing a suitable source URL to OpenCV. 

However, the existence of an IP-camera input path does not mean that N-ONE implements a complete centralized IP-camera management platform. 

## **3.7 Operational Scope** 

The operational scope is intentionally focused on a **controlled local or small demonstration environment** . 

The current architecture is based around a single Streamlit application process. 

Within this process, the application manages: 

- User interface 

- Session state 

- Frame acquisition 

- Face-processing operations 

- In-memory caches 

- File writes 

- Result presentation 

This architecture is appropriate for development, academic demonstration, and controlled evaluation. 

It is not equivalent to a distributed surveillance infrastructure. 

### **3.7.1 Single-Process Architecture** 

The current application does not establish an independent service for every camera or processing operation. 

Instead, the Streamlit application manages the major workflow within the application process. 

Consequently, the current scope does not claim unlimited concurrent processing capacity. 

### **3.7.2 Small-Scale Demonstration** 

The system is suitable for demonstrating the complete workflow using controlled sources such as: 

- Laptop webcam 

- Browser camera 

- Test videos 

- Selected IP/RTSP sources 

- Evaluation images 

Large-scale institutional deployment is outside the current scope. 

## **3.8 Multi-Camera Scope** 

N-ONE can process a camera source when an appropriate source is provided. 

However, the project does **not** currently implement a centralized multi-camera orchestration service. 

The following capabilities are outside the current scope: 

- Central camera registry 

- Distributed camera workers 

- Automatic camera discovery 

- Independent processing service per camera 

- Centralized camera health monitoring 

- Load balancing across cameras 

- Large-scale simultaneous stream management 

Therefore, the project should be described as supporting camera input rather than as a complete enterprise multi-camera surveillance platform. 

## **3.9 AI and Computer-Vision Scope** 

The AI scope of N-ONE covers the use of pretrained or classical computer-vision components rather than training a new neural network from scratch. 

The project contains two conceptually different recognition routes. 

### **3.9.1 OpenCV Fallback Scope** 

The active fallback path is CPU-oriented and uses OpenCV-based processing. 

The implementation can use: 

- Haar-based face detection 

- Profile/frontal detection 

- HOG-related processing 

- CLAHE-related image preprocessing 

This route is intended to provide operational functionality when the full deep-learning environment is unavailable. 

### **3.9.2 DeepFace-Compatible Scope** 

When compatible dependencies are installed, the full runtime can expose recognition models through the DeepFace-compatible interface. 

The project/evaluation environment includes models such as: 

- FaceNet 

- FaceNet512 

- ArcFace 

The exact availability of a model depends on the configured environment. 

### **3.9.3 No New Neural-Network Training** 

An important scope boundary is that N-ONE does **not** train a new face-recognition neural network from scratch. 

The recognition functionality uses existing recognition models or the implemented OpenCV fallback. 

The project therefore focuses on: 

- Model integration 

- Configuration 

- Enrollment 

- Recognition 

- Threshold calibration 

- Benchmark evaluation 

rather than neural-network training. 

## **3.10 Recognition Scope** 

The recognition process consists conceptually of several stages: 

**Face Detection → Representation/Feature Processing → Comparison → Distance/Similarity → Threshold Decision** 

The scope includes the configuration and use of these stages according to the available backend. 

The system can use a configured recognition model, detector, metric, and threshold where supported. 

### **3.10.1 Recognition Threshold Scope** 

The threshold is part of the recognition configuration. 

A threshold determines whether a comparison is sufficiently close to be treated as an accepted match. 

The project allows threshold values to be evaluated experimentally. 

However, a single threshold should not be treated as universally optimal for all environments. 

### **3.10.2 Recognition Metric Scope** 

The project supports configured distance/similarity metrics through its recognition interface. 

The benchmark work uses cosine-based comparison in the evaluated configurations. 

The scope therefore includes experimental comparison under a defined metric rather than claiming that every available metric has been exhaustively evaluated. 

## **3.11 Performance Scope** 

Performance analysis is part of the project, but it is limited to the environments and datasets actually tested. 

Performance can be considered through measurements such as: 

- Processing latency 

- Approximate FPS 

- Model initialization 

- Hardware utilization where measured 

The project does not claim a universal application FPS. 

Actual performance depends on: 

- CPU/GPU 

- Input resolution 

- Video source 

- Model 

- Detector 

- Number of faces 

- Processing pipeline 

- Operating environment 

Therefore, benchmark performance should be presented as **measured under the stated test conditions** . 

## **3.12 Data and Storage Scope** 

N-ONE uses local file-based storage for several types of project information. 

The current scope includes local storage for: 

- Staff profiles 

- Victim profiles 

- Unknown-person data 

- Unknown sightings 

- Victim sightings 

- Audit records 

- Evaluation metadata 

- Evaluation results 

CSV files provide a simple and inspectable mechanism for storing structured records during the academic development stage. 

### **3.12.1 Unknown-Person Storage** 

Unknown observations are maintained through local data structures and CSV records. 

The project includes information such as: 

- Unknown identifier 

- Observation 

- Sighting information 

- Relevant contextual information 

The scope is local unknown-person continuity rather than a centralized identity service. 

### **3.12.2 Victim Sighting Storage** 

Victim Search can produce structured sighting information. 

The scope includes recording available information such as: 

- Victim 

- Timestamp 

- Camera location 

- Recognition information 

- Sighting history 

This allows subsequent review of previous observations. 

### **3.12.3 Audit Logging** 

The project includes CSV-based audit/logging mechanisms. 

The purpose is to provide a reviewable record of relevant application activity. 

However, this is not equivalent to a tamper-resistant enterprise Security Information and Event Management (SIEM) system or a centralized security-event database. 

## **3.13 Security Scope** 

Security is implemented at the application level. 

The current security scope includes: 

- Secret configuration 

- Authentication 

- Role gating 

- Failed-login lockout 

- Logout 

- Administrator-only destructive actions 

- Separation of administrative controls from Operator workflows 

These controls establish a basic security boundary for the application. 

### **3.13.1 Secret Loading** 

The application expects configured secret values for authentication. 

The project supports environment/secret-based configuration rather than requiring credentials to be hard-coded into the application source. 

### **3.13.2 Authentication Lockout** 

Repeated failed attempts can trigger a temporary lockout. 

This provides a basic defense against repeated credential attempts. 

### **3.13.3 Role Protection** 

Administrator-specific controls are hidden or restricted from Operators. 

This reduces the possibility of routine Operators accessing management functions. 

## **3.14 Security Features Outside Current Scope** 

Several enterprise-grade security controls are intentionally outside the current implementation. These include: 

- Password hashing infrastructure 

- Encrypted biometric images 

- Encrypted CSV files 

- Database-level encryption 

- TLS certificate management 

- Enterprise SSO 

- External identity federation 

- Multi-factor authentication 

- Centralized security-event storage 

- SIEM integration 

- Hardware security modules 

- Enterprise key management 

- Full audit immutability 

Therefore, the current security implementation should be described as **prototype/application-level security** , not as a complete production security architecture. 

## **3.15 Dataset Scope** 

The benchmark dataset is deliberately limited in size and is primarily designed for controlled evaluation rather than population-scale validation. 

The established benchmark contains: 

|**Dataset Component**|**Current Scope**|
|---|---|
|Victim identities|5|
|Victim enrollment images|11|
|Genuine Victim test images|32|
|Impostor identities|10|
|Impostor images|12|
|Negative trials|60|
|Evaluation type|Still-image|
|Impostor source metadata|LFW|



The 60 negative trials are generated by comparing the available impostor images against the five Victim identities. 

This means the benchmark evaluates whether non-target individuals are incorrectly accepted as the selected Victim. 

## **3.16 Enrollment/Test Separation** 

A major part of the evaluation scope is the separation between enrollment and test data. 

The same image should not be used both to create the reference representation and to evaluate the recognition system. 

The benchmark therefore maintains separate: 

- Enrollment data 

- Genuine Victim test data 

- Impostor/test data 

This provides a more meaningful estimate of recognition behavior than testing against the exact images used for enrollment. 

## **3.17 Public Dataset Scope** 

The available benchmark metadata identifies **LFW (Labeled Faces in the Wild)** as the source associated with the impostor data. 

The use of such public data is limited to the defined evaluation purpose. 

The public dataset should not be interpreted as representative of every surveillance environment. 

Differences can exist between public still images and actual surveillance conditions, including: 

- Camera resolution 

- Lighting 

- Motion 

- Pose 

- Occlusion 

- Background 

- Image compression 

- Population characteristics 

Therefore, benchmark results should be interpreted within the context of the dataset used. 

## **3.18 Evaluation Scope** 

The evaluation workspace is intended to measure face-recognition behavior under controlled conditions. 

The current evaluation scope includes: 

- Dataset validation 

- Enrollment/test separation 

- Model comparison 

- Threshold comparison 

- TP measurement 

- TN measurement 

- FP measurement 

- FN measurement 

- Precision 

- Recall 

- F1-score 

- FAR 

- FRR 

- Latency measurement 

The evaluation therefore focuses primarily on the **Victim Search recognition problem** . 

## **3.19 Multi-Frame Evaluation Scope** 

Multi-frame confirmation is an identified evaluation area, but the current evidence does not establish a measured multi-frame result because suitable labeled video-sequence data is not available. 

Therefore, the scope does **not** claim measured accuracy improvements from: 

- 1-frame confirmation 

- 3-frame confirmation 

- 5-frame confirmation 

Instead, the system records multi-frame evaluation as unavailable where appropriate. 

This prevents unsupported claims about temporal confirmation performance. 

## **3.20 Staff Recognition Evaluation Scope** 

Although Staff recognition is functionally implemented, a complete Staff-specific recognition benchmark is not established within the current evidence. 

Therefore, the scope distinction is: 

**Implemented:** Staff recognition workflow. 

**Not established:** Comprehensive quantitative Staff recognition accuracy. 

This distinction is important because a feature being implemented does not automatically mean that its performance has been experimentally validated to the same degree as another subsystem. 

## **3.21 Unknown Re-Identification Evaluation Scope** 

Unknown-person re-identification is implemented as a functional mechanism. 

However, a comprehensive quantitative benchmark establishing: 

- Unknown Re-ID accuracy 

- Identity-switch rate 

- IDF1 

- MOTA 

- Track fragmentation 

- Cross-camera tracking performance 

is outside the current established scope. 

The project therefore documents Unknown Re-ID as an implemented operational capability rather than as a fully benchmarked tracking research system. 

## **3.22 Threat-Detection Evaluation Scope** 

Threat detection is implemented using the project's current heuristic/visual processing approach. 

However, the current scope does not establish a comprehensive threat-detection benchmark covering a large and diverse dataset. 

Therefore, the project does not claim experimentally verified: 

- Weapon detection accuracy 

- Fire detection accuracy 

- Precision 

- Recall 

- mAP 

- False alarm rate 

for a general real-world threat-detection population unless those measurements are separately established. 

## **3.23 User Scope** 

N-ONE currently targets two categories of application users. 

#### **Administrator** 

Responsible for: 

- System configuration 

- Subject registration 

- Model settings 

- Administrative management 

#### **Operator** 

##### Responsible for: 

- Monitoring 

- Victim Search 

- Recognition 

- Reviewing unknown observations 

- Reviewing logs 

The project does not currently implement a large hierarchy of organizational roles such as: 

- Super Administrator 

- Security Supervisor 

- Investigator 

- Auditor 

- Database Administrator 

- System Engineer 

Such role expansion can be considered future work. 

## **3.24 Deployment Scope** 

The current deployment scope is primarily: 

##### **Local / Laboratory / Academic Demonstration Environment** 

The system is suitable for: 

- Development 

- Testing 

- Controlled demonstrations 

- Academic evaluation 

- Small-scale local surveillance experiments 

It is not currently scoped as a fully distributed enterprise surveillance platform. 

## **3.25 Scalability Scope** 

Scalability is limited by the current single-process architecture and local storage model. 

The project does not currently establish scalability for: 

- Hundreds of simultaneous cameras 

- Large distributed deployments 

- Multiple geographically separated sites 

- High-volume centralized biometric databases 

- Cloud-native processing clusters 

Such capabilities would require additional architecture, infrastructure, database design, message queues, distributed workers, and resource management. 

## **3.26 Privacy Scope** 

The project recognizes that facial information and surveillance records can involve privacysensitive data. 

The current technical scope includes some controls through: 

- Authentication 

- Role separation 

- Controlled enrollment 

- Target restriction 

- Local data handling 

However, privacy governance is broader than application code. 

The following are not fully established by the current project: 

- Formal biometric-data retention policy 

- Institutional privacy policy 

- Consent-management framework 

- Automated data-deletion policy 

- Data-subject access workflow 

- Formal privacy impact assessment 

- Legal compliance certification 

Therefore, the project should not claim complete privacy compliance solely from its implemented technical controls. 

## **3.27 Out-of-Scope Areas** 

The following areas are outside the currently established implementation or evaluation scope. 

#### **3.27.1 Enterprise Multi-Camera Orchestration** 

No centralized distributed camera-management platform is implemented. 

#### **3.27.2 Large-Scale Production Deployment** 

The project does not establish production scalability for large surveillance networks. 

#### **3.27.3 Complete Staff Accuracy Benchmark** 

Staff recognition is implemented, but comprehensive accuracy evidence is not established. 

#### **3.27.4 Complete Unknown Re-ID Benchmark** 

Unknown tracking is implemented, but comprehensive tracking metrics are not established. 

#### **3.27.5 Comprehensive Threat-Detection Benchmark** 

Threat heuristics are implemented, but general-purpose threat-detection accuracy is not established. 

#### **3.27.6 Multi-Frame Recognition Benchmark** 

Suitable labeled sequence data is not available for a measured multi-frame comparison. 

#### **3.27.7 Enterprise Identity Federation** 

SSO, LDAP/Active Directory federation, OAuth-based enterprise identity, and similar infrastructure are outside the current implementation. 

#### **3.27.8 Advanced Data Encryption** 

Encrypted biometric images and encrypted CSV storage are outside the current implementation. 

#### **3.27.9 TLS Infrastructure** 

Production TLS/certificate management is outside the current application scope. 

#### **3.27.10 Legal Compliance Certification** 

The project does not establish legal compliance or regulatory certification for real-world surveillance deployment. 

#### **3.27.11 Neural-Network Training** 

Training a new face-recognition model from scratch is outside the project scope. 

#### **3.27.12 Institutional Academic Information** 

Institution-specific information such as final guide details, student code, publication information, plagiarism report, and other administrative academic inputs are not established by the repository and therefore should not be fabricated. 

## **3.28 Scope Boundary: Implemented vs Evaluated vs Future** 

A useful way to understand N-ONE's scope is to divide capabilities into three categories. 

|**Category**|**Meaning**|**Examples**|
|---|---|---|
|**Implemented**|Function exists in the application|Authentication, Victim Search,<br>Staff recognition, Unknown<br>tracking|



|**Evaluated**|Function has measurable experimental<br>evidence|Victim face-recognition<br>benchmark|
|---|---|---|
|**Future/Not**|Capability is possible or desirable but|Large-scale multi-camera|
|**Established**|not sufficiently implemented/evaluated|orchestration, complete threat<br>benchmark|



This distinction prevents the project report from confusing software functionality with experimentally validated performance. 

## **3.29 Scope Summary** 

The current scope of N-ONE can be summarized as follows: 

**N-ONE is a locally deployable, Streamlit-based AI-assisted surveillance prototype designed for controlled monitoring and academic evaluation. It supports authenticated Administrator and Operator workflows, controlled Staff and Victim enrollment, target-restricted Victim Search, registered-person recognition, unknown-person tracking, heuristic threat monitoring, local video processing, location-aware sighting records, CSV-based audit information, and experimental face-recognition benchmarking.** 

The project intentionally does not claim to be a complete enterprise surveillance infrastructure. Its current scope does not establish large-scale multi-camera orchestration, comprehensive Staff recognition evaluation, quantitative Unknown Re-ID performance, comprehensive threat-detection accuracy, encrypted biometric storage, enterprise identity federation, or legal compliance certification. 

The most important scope boundary is the distinction between **what N-ONE implements and what N-ONE has experimentally demonstrated** . A feature can exist in the software without having a complete accuracy benchmark. Similarly, a benchmark result represents the tested dataset, model, threshold, and environment rather than universal real-world performance. 

Therefore, the scope of N-ONE is best characterized as an **integrated academic prototype and evaluation platform for AI-assisted surveillance** , with a particular emphasis on controlled Victim Search, measurable face-recognition experiments, operator review, structured evidence, and transparent documentation of limitations. 

## **CHAPTER 4 – PROBLEM DEFINITION** 

### **4.1 Introduction** 

Modern surveillance systems generate a continuous stream of visual information from cameras, webcams, recorded videos, and other sources. The primary difficulty is not only collecting this information but also identifying which observations are relevant, connecting them with appropriate contextual information, and presenting the results to an operator in a consistent and reviewable manner. 

In a conventional workflow, an operator may need to perform several activities independently: 

1. Monitor a video feed. 

2. Identify a person visually. 

3. Compare the person with a registered profile. 

4. Determine the camera/location. 5. Record the observation time. 6. Maintain notes about repeated appearances. 

7. Review suspicious visual events. 

8. Store evidence for later investigation. 

When these activities are distributed across separate applications or performed manually, information can become fragmented. A face may be identified in one tool, the camera location may be recorded elsewhere, and incident information may be maintained separately. This makes it difficult to construct a consistent timeline of observations. 

N-ONE addresses this problem by integrating these activities into a single operator-oriented workflow. However, the project does not attempt to eliminate the inherent limitations of computer vision. Instead, it aims to make the processing, results, contextual information, and limitations more structured and reviewable. 

## **4.2 Existing Surveillance Problem** 

### **4.2.1 Fragmented Surveillance Workflow** 

Traditional surveillance review can involve several independent activities: 

**Camera Monitoring → Manual Identification → Manual Notes → Separate Evidence Storage → Later Review** 

This workflow can create repeated manual effort. 

For example, an operator searching for a particular person may need to: 

- Watch multiple video feeds. 

- Pause or replay footage. 

- Compare the person's appearance manually. 

- Record the camera location. 

- Record the timestamp. 

- Maintain a separate list of previous sightings. 

- Review photographs or other evidence independently. 

The lack of integration can make the investigation process slower and more difficult to reproduce. 

N-ONE attempts to address this fragmentation by combining the major steps into one application. 

### **4.2.2 Lack of Target-Specific Search** 

General face recognition and missing-person search are not identical problems. 

In general recognition, the system may attempt to determine which registered identity corresponds to a detected face. 

In a Victim Search scenario, however, the operator already knows the identity being searched for. The question is: 

##### **Does this observation correspond to the selected Victim?** 

This is closer to a target-specific verification problem. 

If the system compares every detected face against every registered profile and simply displays the closest result, an unrelated Staff member or another registered person could potentially be presented as the search target. 

N-ONE addresses this problem by restricting the visible known matching in Victim Search to the selected Victim. 

## **4.3 Recognition Failure Conditions** 

Face recognition is affected by both the quality of the input image and the characteristics of the recognition pipeline. 

A recognition system may perform differently depending on the conditions under which a face was enrolled and subsequently observed. 

The major problem conditions considered by N-ONE include the following. 

### **4.3.1 Illumination Variation** 

Lighting can significantly change the appearance of a face. 

For example: 

- Bright outdoor lighting 

- Low-light environments 

- Backlighting 

- Shadows 

- Uneven illumination 

- Artificial lighting 

can alter the visual characteristics available to the recognition system. 

An enrollment photograph captured under controlled lighting may therefore differ substantially from a surveillance frame captured under poor or changing lighting. 

N-ONE's preprocessing and recognition configuration can help manage some image variation, but they cannot eliminate the underlying environmental problem. 

### **4.3.2 Pose Variation** 

A face viewed directly from the front may contain significantly different visual information from a face viewed from the side. 

Examples include: 

- Frontal face 

- Left profile 

- Right profile 

- Upward-facing face 

- Downward-facing face 

Large pose changes can reduce the similarity between the enrollment representation and the observed representation. 

### **4.3.3 Motion Blur** 

When a person or camera moves during image acquisition, the resulting frame can contain motion blur. 

Blur can reduce the amount of usable facial detail. 

This can lead to: 

- Failure to detect a face 

- Poor feature extraction 

- Increased recognition distance 

- False rejection 

Therefore, recognition performance on static enrollment images cannot automatically be assumed to represent performance on moving video. 

### **4.3.4 Camera Distance** 

As the distance between the subject and camera increases, the number of pixels representing the face may decrease. 

A small face may contain insufficient detail for reliable recognition. 

This creates an important relationship between: 

**Camera → Subject Distance → Face Resolution → Recognition Quality** 

The project therefore cannot guarantee the same recognition performance at every camera distance. 

### **4.3.5 Occlusion** 

A face may be partially hidden by: 

- Masks 

- Sunglasses 

- Hands 

- Hair 

- Helmets 

- Other objects 

- Another person's body 

Partial visibility reduces the information available for recognition. 

N-ONE's recognition pipeline can only operate on the visual information available in the input frame. 

### **4.3.6 Partial Face Visibility** 

A face may be positioned partly outside the camera frame. 

For example, only part of the forehead, eye region, or cheek may be visible. 

Such observations can result in: 

- No valid face detection 

- Poor representation 

- Increased comparison distance 

- False rejection 

This is one reason why controlled enrollment alone cannot guarantee successful recognition in uncontrolled surveillance environments. 

### **4.3.7 Multiple Faces** 

A surveillance frame can contain several people simultaneously. 

This creates a different problem from single-subject enrollment. 

During registration, N-ONE requires exactly one detectable face so that the reference identity is unambiguous. 

During surveillance, multiple faces may legitimately be present. 

The system therefore has to process detected faces individually and apply the appropriate operational-mode logic. 

In Victim Search, the important question is whether one of the detected faces corresponds to the selected target—not whether every visible person should be assigned an identity. 

### **4.3.8 Face Detector Errors** 

Face recognition depends on successful face detection. 

If a detector fails to locate a face, the recognition stage cannot correctly compare it. 

Detection errors can occur because of: 

- Poor lighting 

- Extreme pose 

- Small face size 

- Blur 

- Occlusion 

- Unusual image quality 

Therefore, recognition accuracy is influenced not only by the recognition model but also by the detector. 

### **4.3.9 Enrollment-to-Observation Difference** 

The enrollment image represents the subject under one set of conditions. 

The surveillance image may represent the same person under another set of conditions. 

For example: 

##### **Enrollment:** 

Good lighting + frontal face + high resolution 

##### **Observation:** 

Low lighting + side pose + motion blur + lower resolution 

Even though both images belong to the same person, their visual representations may be substantially different. 

This is an important source of false-negative recognition results. 

## **4.4 Controlled Enrollment as a ProblemMitigation Mechanism** 

N-ONE attempts to reduce some recognition problems through controlled enrollment. 

The registration process requires: 

##### **Exactly one detectable face** 

and stores a padded face crop. 

This reduces ambiguity caused by: 

- Multiple people in the enrollment image 

- Excessive background 

- Uncontrolled subject framing 

However, controlled enrollment only improves the quality of the reference data. 

It does not eliminate problems occurring during live observation. 

Therefore: 

**Better enrollment improves the input conditions but does not guarantee recognition under arbitrary surveillance conditions.** 

## **4.5 False Positive and False Negative Risks** 

Two of the most important problems in face-based Victim Search are **false positives** and **false negatives** . 

### **4.5.1 False Positive** 

A false positive occurs when an individual who is **not the selected Victim** is accepted as the Victim. 

For example: 

**Selected Target:** Victim A 

**Actual Person:** Impostor B 

**System Result:** Victim A Found 

This is a serious recognition error because the system has incorrectly associated an unrelated person with the selected target. 

In mathematical evaluation terms: 

FP=Non-target observation incorrectly accepted as targetFP = \text{Non-target observation incorrectly accepted as target} 

For Victim Search, reducing false acceptance is particularly important because an incorrect target match can misdirect an operator's attention. 

### **4.5.2 False Negative** 

A false negative occurs when the actual selected Victim is present but the system does not accept the observation. 

For example: 

**Selected Target:** Victim A 

**Actual Person:** Victim A 

**System Result:** No Match 

This can happen because of: 

- Poor lighting 

- Pose changes 

- Occlusion 

- Motion blur 

- Camera distance 

- Threshold selection 

- Detector failure 

- Differences between enrollment and observation 

Formally: 

FN=Genuine target observation incorrectly rejectedFN = \text{Genuine target observation incorrectly rejected} 

A high false-negative rate means the system may miss genuine observations. 

## **4.6 False Positive vs False Negative Trade-Off** 

The recognition threshold influences the balance between false acceptance and false rejection. Conceptually: 

##### **More permissive threshold** 

- → More observations may be accepted 

- → Potentially fewer false negatives 

- → Potentially more false positives 

Conversely: 

##### **More restrictive threshold** 

- → Fewer observations may be accepted 

- → Potentially fewer false positives 

- → Potentially more false negatives 

The exact relationship must be measured experimentally rather than assumed. 

This is why N-ONE evaluates recognition using multiple threshold values. 

## **4.7 Recognition Distance and Threshold Problem** 

In the recognition pipeline, a detected face is represented and compared with an enrolled reference. 

Let: 

- RtR_t = representation of the observed face 

- RvR_v = representation of the selected Victim 

- D(Rt,Rv)D(R_t,R_v) = distance between the two representations 

- τ\tau = configured threshold 

A simplified decision rule is: 

D(Rt,Rv)≤⇒τ Candidate MatchD(R_t,R_v) \leq \tau \Rightarrow \text{Candidate Match} 

and: 

⇒ D(Rt,Rv)>τ RejectD(R_t,R_v) > \tau \Rightarrow \text{Reject} 

The threshold therefore directly affects the decision boundary. 

However, a distance value itself is not a universal “percentage of identity.” It is a model- and metric-dependent measurement. 

Therefore, N-ONE should report the distance and decision threshold rather than converting the raw distance into an unsupported “match percentage.” 

## **4.8 Unsafe Fallback Identity Problem** 

The project contains a specific safety consideration around fallback recognition. 

The full neural recognition route can provide a configured representation-based comparison when the required runtime is available. 

The fallback route uses OpenCV-based processing. 

The project intentionally avoids treating the fallback identity decision as equivalent to the neural recognition result for visible Victim identification when the neural runtime is unavailable. 

This is important because the fallback processing path does not automatically provide the same identity-recognition evidence as the configured deep-learning recognition models. 

Therefore, the system should avoid presenting an unsupported fallback result as a definitive Victim identification. 

This is an example of a design decision based on **evidence boundaries** rather than simply attempting to maximize the number of displayed matches. 

## **4.9 Benchmark-Based Recognition Problem** 

Another problem addressed by N-ONE is the difficulty of determining whether a recognition configuration is actually suitable. 

Simply observing that a model produces a visually plausible match is not enough. 

A proper evaluation requires: 

1. Separate enrollment data. 

2. Genuine target test data. 

3. Impostor/non-target test data. 

4. Multiple comparisons. 

5. Threshold analysis. 

6. Quantitative metrics. 

The project therefore evaluates recognition through measurable quantities such as: 

- TP 

- TN 

- FP 

- FN 

- Precision 

- Recall 

- F1 

- FAR 

- ● FRR 

## **4.10 Recognition Evaluation Metrics** 

### **4.10.1 Precision** 

Precision measures how many accepted positive predictions were actually correct. 

Precision=TPTP+FPPrecision = \frac{TP}{TP+FP} 

A low precision value indicates that a significant proportion of accepted matches may be incorrect. 

### **4.10.2 Recall** 

Recall measures how many genuine target observations were successfully accepted. 

Recall=TPTP+FNRecall = \frac{TP}{TP+FN} 

A low recall value indicates that the system is missing a substantial number of genuine target observations. 

### **4.10.3 F1-Score** 

F1 combines precision and recall. 

F1=2×Precision×RecallPrecision+RecallF1 = 2 \times \frac{Precision \times Recall} {Precision + Recall} 

This provides a single measure of the balance between the two. 

### **4.10.4 False Acceptance Rate** 

For target verification: 

FAR=FPFP+TNFAR = \frac{FP}{FP+TN} 

FAR is especially important for Victim Search because it measures how frequently non-target observations are incorrectly accepted. 

### **4.10.5 False Rejection Rate** 

FRR=FNFN+TPFRR = \frac{FN}{FN+TP} 

FRR indicates how frequently genuine target observations are rejected. 

Together, FAR and FRR help describe the recognition system's decision behavior. 

## **4.11 Unknown-Person Problem** 

A surveillance system cannot assume that every detected person has a known identity. 

In N-ONE, a person can be treated as **unknown** when the available recognition process does not produce an accepted match against the appropriate registered profiles. 

However, the term “unknown” must be interpreted carefully. 

An unknown identifier does **not** mean: 

“This is a specific real-world person whose identity is unknown.” 

Instead, it means: 

**“This observation has been assigned a local representation/identifier because it did not match the currently available registered identities.”** 

## **4.12 Unknown Re-Identification Problem** 

Unknown Re-ID addresses a different problem from Victim Search. 

#### **Victim Search** 

Question: 

##### **Does this observation correspond to the selected known Victim?** 

#### **Unknown Re-ID** 

Question: 

##### **Does this new unknown observation appear sufficiently similar to a previously stored unknown observation?** 

The second question does not establish a person's real-world identity. 

For example: 

**Observation 1 → Unknown_003** 

Later: 

**Observation 2 → Similar to Unknown_003** 

The system can associate the second observation with Unknown_003. 

This means: 

The two observations appear to represent the same locally tracked unknown. 

It does **not** mean: 

The system has discovered the person's real name. 

## **4.13 Unknown Re-ID Failure Conditions** 

Unknown-person matching can itself produce errors. 

#### **False Association** 

Two different people may appear sufficiently similar and be assigned the same unknown identifier. 

#### **Identity Fragmentation** 

The same person may appear sufficiently different across observations and receive multiple unknown identifiers. 

This can occur because of: 

- Different lighting 

- Different pose 

- Occlusion 

- Clothing changes 

- Camera angle 

- Image quality 

- Different facial visibility 

Therefore, unknown re-identification is also a probabilistic similarity problem rather than guaranteed identity tracking. 

## **4.14 Threat-Detection Problem** 

The threat-detection branch addresses a different visual-analysis problem. 

Instead of asking: 

“Who is this person?” 

it asks: 

“Does the visual input contain a pattern that resembles one of the configured threat indicators?” 

The current implementation uses visual heuristics involving features such as: 

- Contours 

- Shape characteristics 

- Elongated regions 

- HSV/color-based analysis 

- Warm-color regions 

The resulting labels include indicators such as: 

- Possible weapon 

- Possible fire 

These labels should be interpreted as **heuristic alerts** , not confirmed classifications. 

## **4.15 Weapon-Like Object Detection Problem** 

An elongated contour can correspond to many different objects. 

For example, an elongated region might represent: 

- A tool 

- A mobile device 

- A stick 

- A piece of furniture 

- A shadow 

- A genuine weapon 

A contour-based algorithm does not inherently understand the semantic identity of the object. Therefore: 

Elongated contour≠!Confirmed weapon\text{Elongated contour} \neq \text{Confirmed weapon} 

The system can only indicate that the visual pattern satisfies the implemented heuristic. 

This is why human review is necessary before treating the result as an operational threat. 

## **4.16 Fire-Like Region Detection Problem** 

Similarly, a warm or orange region can occur in many non-fire situations. 

For example: 

- Clothing 

- Lighting 

- Reflections 

- Decorative objects 

- Sunlight 

- Background elements 

may produce color patterns similar to those targeted by a simple HSV mask. 

Therefore: 

Warm-color region≠!Confirmed fire\text{Warm-color region} \neq \text{Confirmed fire} 

The N-ONE implementation treats such results as possible fire-like regions requiring review. 

## **4.17 Separation of Face and Threat Processing** 

Another problem addressed by the architecture is avoiding unnecessary coupling between different visual-analysis tasks. 

When the application is operating in Threat Detection Mode: 

##### **Face comparison is skipped.** 

Instead, the frame is processed through the threat-analysis branch. 

This prevents face-recognition configuration from being incorrectly interpreted as threat-detection configuration. 

The conceptual separation is: 

#### **Face Modes** 

**Frame → Face Detection → Representation → Comparison → Threshold → Identity Status** 

#### **Threat Mode** 

##### **Frame → Visual Processing → Contours/HSV Heuristics → Threat Indicator** 

This separation simplifies interpretation and allows the two subsystems to be evaluated independently. 

## **4.18 Operational Context Problem** 

A recognition result without context can be difficult to interpret. 

For example: 

##### **“Victim Found”** 

does not provide sufficient information by itself. 

An operator may also need: 

- Which Victim? 

- At what time? 

- At which camera? 

- What recognition distance? 

- Which model/backend? 

- Was this a repeated sighting? 

- What image produced the result? 

N-ONE therefore associates available contextual information with the result. 

This transforms the output from a simple Boolean decision into a more reviewable event. 

## **4.19 Logging and Evidence Problem** 

A surveillance system should not rely entirely on transient UI messages. 

If an event disappears after the frame is processed, it becomes difficult to review later. 

N-ONE addresses this problem through structured local logging. 

Relevant information can be recorded in CSV-based files, including Victim sightings and unknownperson observations. 

This provides a persistent representation of important system events. 

However, CSV logging does not provide the tamper resistance, centralized management, or forensic guarantees of a specialized security-event management system. 

## **4.20 Human Decision-Making Problem** 

Automated recognition can provide computational assistance, but the system cannot understand the complete real-world context of an event. 

For example, an algorithm may report: 

##### **Possible weapon** 

but the operator may observe contextual information indicating that the object is a harmless tool. 

Similarly, a face-recognition system may produce a target match while the operator notices significant differences or poor image quality. 

Therefore, N-ONE treats automated outputs as **decision-support information** rather than fully autonomous decisions. 

The human operator remains responsible for: 

- Reviewing results 

- Considering context 

- Confirming important observations 

- Escalating according to procedure 

- Handling false positives 

- Handling false negatives 

## **4.21 Formal Problem Statement** 

The N-ONE surveillance problem can be formally described using the following variables. 

Let: 

- FF = input video frame or image 

- MM = selected operational mode 

- VV = optional selected Victim profile 

- LL = camera/location information 

- RR = representation or feature-extraction function 

- DD = distance/comparison function 

- τ\tau = recognition threshold 

- KK = relevant known-profile set 

- UU = unknown-person representation store 

- TT = threat-analysis function 

The system must process FF according to MM and produce an appropriate status while maintaining the distinction between: 

1. Known target identity 

2. Other registered identities 

3. Unknown observations 

4. Possible threat indicators 

## **4.22 Formal Face-Processing Model** 

For a detected face xx, the system first obtains a representation: 

rx=R(x)r_x = R(x) 

For a selected Victim VV, let: 

rV=R(V)r_V = R(V) 

The system then calculates: 

d=D(rx,rV)d = D(r_x,r_V) 

where dd represents the configured distance between the observed face and the selected Victim representation. 

The decision can then be represented as: 

Decision(x,V)≠{Match,d≤τReject,d>τDecision(x,V)≠ \begin{cases} Match, & d \leq \tau \\ Reject, & d > \tau \end{cases} 

The actual implementation details depend on the selected recognition backend and metric. 

## **4.23 Formal Victim Search Requirement** 

For Victim Search, the known comparison set should be restricted to the selected target. 

If: 

V=Selected VictimV = \text{Selected Victim} 

then the visible target-matching operation should effectively evaluate: 

Kvictim={V}K_{victim} = \{V\} 

rather than: 

K={V1,V2,…,S1,S2,…}K = \{V_1,V_2,\ldots,S_1,S_2,\ldots\} 

This means that the system should not select another registered identity simply because it has the smallest distance to the observed face. 

The key requirement is: 

**The Victim Search result must remain semantically tied to the selected Victim.** 

## **4.24 Formal Unknown Re-ID Model** 

For an unmatched face xx: 

rx=R(x)r_x = R(x) 

The system can compare rxr_x with previously stored unknown representations: 

U={u1,u2,…,un}U = \{u_1,u_2,\ldots,u_n\} 

If: 

D(rx,ui)≤τuD(r_x,u_i) \leq \tau_u 

then the new observation may be associated with the corresponding local unknown identifier. Otherwise, a new unknown identifier can be created. 

This can be represented as: 

UnknownDecision(x)≠{Ui,D(rx,ui)≤τuUnew,otherwiseUnknownDecision(x)≠ \begin{cases} U_i, & D(r_x,u_i)\leq\tau_u \\ U_{new}, & \text{otherwise} \end{cases} 

This is a local re-identification mechanism, not a verified identity-resolution mechanism. 

## **4.25 Formal Threat-Processing Model** 

When: 

M=ThreatDetectionM = ThreatDetection 

the system does not perform Victim/Staff face comparison. 

Instead: 

ThreatResult=T(F)ThreatResult = T(F) 

where TT represents the implemented contour and color-based threat heuristic. 

The output can contain statuses such as: 

T(F)→{Possible WeaponPossible FireNo Detected Threat IndicatorT(F) \rightarrow \begin{cases} Possible\ Weapon\\ Possible\ Fire\\ No\ Detected\ Threat\ Indicator \end{cases} 

The result represents a visual heuristic and requires human interpretation. 

## **4.26 Location and Evidence Association** 

For an operational result RsR_s, the contextual event can be represented as: 

E=(Rs,L,t,I)E = (R_s,L,t,I) 

where: 

- RsR_s = system result/status 

- LL = camera/location 

- tt = timestamp 

- II = available image or recognition information 

This structure allows an observation to be considered as an event rather than as an isolated prediction. 

For example: 

##### **Victim Found + Camera A + 10:32 AM + Recognition Evidence** 

provides more useful context than: 

##### **Victim Found** 

alone. 

## **4.27 Core Problem of N-ONE** 

The central problem addressed by N-ONE can therefore be summarized as: 

**How can a local AI-assisted surveillance system process visual input, identify a selected registered Victim or other registered person when supported by the configured recognition pipeline, maintain repeat-unknown context, identify possible threat-like visual patterns, and preserve location-aware evidence while minimizing incorrect target presentation and clearly communicating the limitations of automated decisions?** 

This problem contains several interconnected sub-problems: 

1. **Input Problem** – acquiring usable frames. 

2. **Detection Problem** – locating relevant faces or visual regions. 

3. **Representation Problem** – converting detected faces into usable features/embeddings. 

4. **Comparison Problem** – measuring similarity between observations and references. 

5. **Decision Problem** – selecting an appropriate threshold. 

6. **Target Restriction Problem** – ensuring Victim Search remains tied to the selected target. 

7. **Unknown Re-ID Problem** – associating repeated unknown observations. 

8. **Threat Analysis Problem** – detecting possible threat-like visual patterns. 

9. **Context Problem** – associating results with time and location. 

10. **Evidence Problem** – preserving results for later review. 

11. **Security Problem** – controlling access to the system and its data. 

12. **Evaluation Problem** – determining whether the recognition configuration performs adequately under controlled test conditions. 

## **4.28 Problem-Solution Relationship** 

##### **Problem N-ONE Approach** 

|Fragmented monitoring workflow|Integrated Streamlit dashboard|
|---|---|
|Uncontrolled enrollment|Single-face registration validation|
|Excess background in references|Padded face-crop storage|
|Unfocused Victim Search|Selected-target restriction|
|Unknown repeated observations|Unknown-person local re-identification|
|Missing location context|Camera/location field|
|Lack of persistent event information|CSV-based sighting/audit logs|



|Recognition uncertainty|Threshold-based comparison|
|---|---|
|Model-selection uncertainty|Dedicated evaluation workspace|
|False positive risk|Impostor testing and FAR measurement|
|False negative risk|Genuine-target testing and FRR measurement|
|Threat visual indicators|Contour/HSV heuristic branch|
|Unauthorized administration|Admin/Operator role separation|
|Experimental changes affecting<br>production|Separate evaluation and production<br>configuration|
|Unsupported identity certainty|Human-in-the-loop review|



## **4.29 Problem Boundaries** 

The problem definition intentionally excludes several broader problems. 

N-ONE does not attempt to solve: 

- Universal human identification. 

- Perfect face recognition under arbitrary conditions. 

- Autonomous surveillance decision-making. 

- Guaranteed weapon classification. 

- Guaranteed fire detection. 

- Large-scale distributed camera management. 

- Complete biometric identity management. 

- Legal or regulatory compliance through software alone. 

These exclusions are important because solving the narrower engineering problem is more measurable and appropriate for the project's current architecture and evaluation resources. 

## **4.30 Final Problem Definition** 

The problem addressed by N-ONE is therefore not simply: 

**“Recognize faces using AI.”** 

It is a broader systems problem: 

**To design an integrated AI-assisted surveillance workflow that can process visual inputs according to the selected operational mode, perform controlled face comparison for registered subjects, restrict Victim Search to the selected target, maintain local context for repeated unknown observations, identify possible threat-like visual patterns through implemented heuristics, associate results with time and camera location, and preserve reviewable records while explicitly accounting for false positives, false negatives, environmental limitations, and the uncertainty of automated visual decisions.** 

The system must satisfy the following core principle: 

Automated Result+Context+Evidence+Human Review≠!Guaranteed Truth 

This principle defines the practical boundary of N-ONE. The project provides computational assistance and measurable evidence, but the final interpretation of a surveillance event remains dependent on the quality of the input, the selected model and threshold, environmental conditions, available evidence, and authorized human review. 

## . **CHAPTER 5 – BENEFITS OF THE PROJECT** 

### **5.1 Introduction** 

N-ONE is designed as an integrated AI-assisted surveillance platform that combines subject registration, face-based recognition, target-restricted Victim Search, unknown-person reidentification, threat-oriented visual analysis, location-aware monitoring, structured logging, and experimental model evaluation within a single application. 

The primary benefit of this architecture is that the operator does not have to treat every activity as an independent process. Registration, monitoring, recognition, contextual information, and reviewable records are connected through a common workflow. 

However, these benefits must be interpreted within the technical scope of the project. N-ONE is an academic and experimental prototype, and the existence of a feature does not automatically establish universal accuracy, production scalability, legal compliance, or guaranteed real-world performance. 

## **5.2 Integrated Operator Workflow** 

One of the major benefits of N-ONE is the integration of several surveillance functions into a single Streamlit dashboard. 

A typical workflow can be represented as: 

**Authentication → Profile Selection/Registration → Operational Mode → Video Input → Detection → Analysis → Result → Logging → Operator Review** 

Without an integrated workflow, an operator may need separate tools for: 

- Managing registered subjects 

- Viewing camera feeds 

- Performing face recognition 

- Recording observations 

- Reviewing unknown individuals 

- Analyzing suspicious visual events 

- Maintaining evidence 

N-ONE brings these functions into one application environment. 

This reduces unnecessary switching between independent tools and creates a more consistent operational process. 

The benefit is primarily **workflow integration** , not a guarantee that the system will perform faster than every alternative implementation. 

## **5.3 Controlled Subject Registration** 

N-ONE provides a structured registration process for Staff and Victim profiles. 

During registration, the system expects the image to contain exactly one detectable face. 

This provides several advantages. 

#### **5.3.1 Reduced Enrollment Ambiguity** 

If an image contains multiple people, it may be unclear which person should represent the registered identity. 

By requiring exactly one detectable face, N-ONE reduces this ambiguity. 

#### **5.3.2 More Consistent Reference Images** 

The system extracts and stores a padded face crop. 

Instead of using an arbitrary full image containing: 

- Background 

- Multiple objects 

- Unrelated people 

- Excessive surrounding information 

the recognition pipeline receives a more focused reference. 

#### **5.3.3 Predictable Profile Storage** 

Profiles follow a predictable local naming structure, such as: 

- Staff_<name>.jpg 

- Victim_<name>.jpg 

This simplifies profile discovery, inventory management, and local project inspection. 

#### **5.3.4 Improved Dataset Organization** 

Controlled enrollment also makes it easier to distinguish between registered references and later test images during evaluation. 

However, controlled enrollment improves the quality of the reference data; it does **not** eliminate environmental recognition problems during live monitoring. 

## **5.4 Target-Restricted Victim Search** 

Target-restricted Victim Search is one of the most important functional benefits of N-ONE. 

In a general face-recognition system, a detected face may be compared against many registered identities. 

For a Victim Search workflow, however, the operator is normally interested in one particular target. 

N-ONE therefore allows the operator to select a specific Victim before starting the search. 

The workflow becomes: 

**Selected Victim → Camera Input → Face Detection → Target Comparison → Threshold Decision → Victim Result** 

This provides a clear semantic relationship between the search operation and the selected target. 

### **5.4.1 Reduced Identity Confusion** 

Restricting the visible known matching to the selected Victim helps prevent an unrelated Staff member or another registered Victim from being presented as the search target. 

For example: 

**Selected Target:** Victim A 

**Observed Person:** Staff B 

The system should not convert Staff B into a “Victim A Found” result merely because Staff B is a registered person. 

This makes the search workflow more consistent with its intended purpose. 

### **5.4.2 Target-Focused Operator Interface** 

The operator does not need to interpret a large list of unrelated registered identities during a specific Victim search. 

Instead, the interface can focus attention on: 

- Selected Victim 

- Recognition result 

- Camera location 

- Timestamp 

- Recognition distance 

- Sighting history 

This can make the investigation workflow easier to understand. 

## **5.5 Context-Rich Victim Results** 

Another benefit is that N-ONE does not need to limit a Victim result to a simple “match/no-match” status. 

When the selected Victim satisfies the configured recognition conditions, the system can provide additional contextual information. 

This may include: 

- Victim name 

- Profile ID 

- Recognition distance 

- Timestamp 

- Camera location 

- Active recognition model/backend 

- Recognition metric 

- Previous sighting information 

This creates a more informative event representation: 

##### **Who + Where + When + Recognition Evidence** 

rather than: 

**Who** 

## **5.6 Location-Aware Monitoring** 

Camera location is an important part of surveillance context. 

N-ONE allows the operator to provide a camera/location value during monitoring. 

A Victim sighting can therefore be associated with information such as: 

**Victim → Camera Location → Timestamp → Recognition Event** 

This makes the result more useful for subsequent review. 

For example, multiple sightings can be interpreted as a sequence of observations rather than unrelated recognition events. 

The benefit is contextual organization. The location value should not be interpreted as independently verified physical geolocation. 

## **5.7 Repeat-Unknown Context** 

Not every person appearing in a surveillance feed will be present in the registered Staff or Victim inventory. 

N-ONE provides an unknown-person mechanism for such observations. 

Instead of discarding every unmatched observation, the system can store information about an unknown individual and attempt to associate subsequent similar observations with the same local unknown identifier. 

### **5.7.1 Continuity Between Observations** 

Suppose the system creates: 

##### **Unknown_001** 

for an initial observation. 

If a later observation is sufficiently similar according to the implemented matching mechanism, the system can associate it with: 

##### **Unknown_001** 

This provides a basic continuity mechanism. 

### **5.7.2 Unknown Does Not Mean Identified** 

An important benefit of this design is that the system can maintain context without inventing a realworld identity. 

For example: 

##### **Unknown_001** 

means that the application has created a local tracking representation. 

It does not mean: 

##### **“The system knows who this person actually is.”** 

This distinction is important for responsible interpretation. 

## **5.8 Reviewable CSV Audit Trail** 

N-ONE uses structured CSV-based records for relevant application events. 

Examples include records associated with: 

- Unknown persons 

- Unknown sightings 

- Victim sightings 

- Audit information 

This provides a simple and transparent method for reviewing system activity. 

### **5.8.1 Easy Inspection** 

CSV files can be opened using common spreadsheet and data-analysis tools. 

This makes it easier for a student, evaluator, or developer to inspect: 

- Timestamps 

- Locations 

- IDs 

- Recognition information 

- Sighting records 

without requiring a specialized database-management interface. 

### **5.8.2 Academic Reproducibility** 

For an academic project, simple local records can be useful because the evaluator can directly inspect the generated evidence. 

The files can also be used during analysis with tools such as Python and Pandas. 

### **5.8.3 Clear Evidence Trail** 

A structured record is more useful than relying only on temporary dashboard messages. 

For example: 

##### **Dashboard Message:** 

Victim Found 

is temporary. 

A corresponding structured record containing: 

##### **Victim + Location + Timestamp + Recognition Information** 

provides information that can be reviewed later. 

However, CSV logging should not be described as an immutable forensic evidence system or enterprise SIEM. 

## **5.9 Separation of Benchmark and Production Configuration** 

One of the important engineering benefits of N-ONE is the separation between the experimental evaluation environment and the live application configuration. 

This allows the project to test alternative recognition models without automatically replacing the production configuration. 

For example, a benchmark can evaluate: 

- FaceNet 

- FaceNet512 

- ArcFace 

under controlled conditions. 

The results can then be reviewed before considering a production configuration change. 

### **5.9.1 Prevents Silent Configuration Changes** 

Without this separation, an experimental model change could unintentionally alter live application behavior. 

N-ONE instead maintains a distinction between: 

##### **Experimental Configuration** 

and 

##### **Production Configuration** 

This makes testing safer and easier to document. 

### **5.9.2 Supports Evidence-Based Model Selection** 

A model should not be selected only because it appears theoretically suitable. 

The evaluation environment allows model behavior to be examined using measurable evidence such as: 

- TP 

- TN 

- FP 

- FN 

- Precision 

- Recall 

- F1 

- FAR 

- FRR 

- Latency 

This provides a stronger basis for technical discussion. 

## **5.10 Threshold Evaluation Benefit** 

Recognition systems depend heavily on the decision threshold. 

A threshold that is too permissive may increase false acceptance. 

A threshold that is too restrictive may increase false rejection. 

N-ONE's evaluation workflow allows different threshold values to be tested. 

This helps the developer understand how recognition behavior changes as the decision boundary changes. 

The benefit is not that the project automatically discovers a universally optimal threshold. Instead, it provides a mechanism for **controlled threshold analysis** . 

## **5.11 Quantitative Recognition Analysis** 

N-ONE's evaluation framework provides a benefit beyond simple demonstration: it allows recognition behavior to be expressed quantitatively. 

The evaluation can measure: 

#### **True Positive** 

Correct acceptance of a genuine target. 

#### **True Negative** 

Correct rejection of a non-target. 

#### **False Positive** 

Incorrect acceptance of an impostor as the target. 

#### **False Negative** 

Failure to accept the genuine target. 

From these measurements, the project can calculate: 

Precision=TPTP+FPPrecision=\frac{TP}{TP+FP} Recall=TPTP+FNRecall=\frac{TP}{TP+FN} F1=2Precision×RecallPrecision+RecallF1=2\frac{Precision\times Recall}{Precision+Recall} FAR=FPFP+TNFAR=\frac{FP}{FP+TN} FRR=FNFN+TPFRR=\frac{FN}{FN+TP} 

This allows the system to be discussed using measurable evidence rather than subjective visual impressions. 

## **5.12 Improved Understanding of Recognition Errors** 

The evaluation framework also provides a way to understand **how** the system fails. 

A simple demonstration may show that the system successfully recognizes a person. 

However, quantitative evaluation can reveal whether the system: 

- Misses genuine observations 

- Accepts impostors 

- Becomes more permissive at certain thresholds 

- Becomes more restrictive at others 

- Requires significant processing time 

This makes the project more useful from a research and engineering perspective. 

## **5.13 Human-in-the-Loop Operation** 

A major benefit of N-ONE is that the architecture keeps the human operator involved in important decisions. 

The system provides computational assistance, but the operator remains responsible for: 

- Reviewing the result 

- Considering environmental context 

- Confirming important observations 

- Assessing whether escalation is appropriate 

- Interpreting suspicious detections 

- Handling possible false positives and false negatives 

This is particularly important because visual recognition systems cannot fully understand the realworld context of every observation. 

## **5.14 Operator Review of Victim Results** 

When N-ONE produces a Victim Search result, the operator can review the available evidence rather than relying solely on an automated label. 

The operator can consider: 

- Captured image 

- Selected Victim profile 

- Recognition distance 

- Timestamp 

- Camera location 

- Sighting history 

- Model/backend information 

This creates a more transparent decision-support workflow. 

## **5.15 Separate Threat-Detection Workflow** 

Threat detection is handled separately from face recognition. 

This provides an architectural benefit because the two tasks have different objectives. 

#### **Face Recognition** 

Attempts to answer: 

##### **Does the detected face correspond to the relevant registered identity?** 

#### **Threat Detection** 

Attempts to answer: 

##### **Does the frame contain a visual pattern matching the implemented threat heuristic?** 

This separation makes the system easier to understand and allows the recognition and threat components to be evaluated independently. 

## **5.16 Threat-Monitoring Benefit** 

The threat branch provides an additional monitoring signal beyond identity recognition. 

The implemented heuristics can identify visual patterns associated with: 

- Possible elongated weapon-like objects 

- Possible warm fire-like regions 

This can help draw operator attention toward potentially relevant frames. 

However, the benefit is **early visual indication** , not confirmed threat classification. 

For example: 

Possible weapon 

should be interpreted as: 

“The visual pattern satisfies the implemented heuristic and should be reviewed.” 

It should not automatically be interpreted as: 

“A weapon has been conclusively detected.” 

## **5.17 Local Data Handling** 

N-ONE uses predictable local paths for important project data. 

This provides several benefits for a controlled academic environment. 

#### **Easier Inspection** 

Developers can locate profiles, logs, and evaluation files without requiring a remote database. 

#### **Easier Demonstration** 

The project can operate within a controlled local environment. 

#### **Reduced External Dependency** 

The core workflow does not require every piece of operational data to be stored in an external cloud service. 

#### **Reproducibility** 

The project structure can be copied and examined as a complete local application. 

These benefits are particularly relevant for academic development and testing. 

## **5.18 Modular Architecture** 

N-ONE separates major responsibilities into logical modules and workflows. 

These include: 

- Authentication 

- Profile registration 

- Recognition 

- Victim Search 

- Unknown Re-ID 

- Threat detection 

- Logging 

- Evaluation 

- Dashboard presentation 

This modularity provides several engineering benefits. 

#### **Easier Debugging** 

A problem can be isolated to a particular subsystem. 

#### **Easier Testing** 

Individual workflows can be tested independently. 

#### **Easier Future Development** 

Additional recognition models or improved threat algorithms can potentially be introduced without redesigning the entire dashboard. 

#### **Easier Documentation** 

Each subsystem can be explained independently. 

## **5.19 Flexible Recognition Backend** 

N-ONE supports more than one face-processing route. 

The full recognition environment can use DeepFace-compatible models when the necessary dependencies are available. 

The project also contains an OpenCV-based fallback route. 

This provides environmental flexibility. 

For example, if the complete TensorFlow/DeepFace environment cannot be loaded, the application still has an OpenCV-based processing path for supported functionality. 

However, the fallback should not automatically be considered equivalent to the deep-learning recognition models. 

## **5.20 Controlled Computational Requirements** 

The main OpenCV processing path limits frame width to approximately 1280 pixels. 

This can help avoid unnecessary processing overhead from very high-resolution input. 

The application also maintains in-memory known and unknown face caches where appropriate. 

These design choices can reduce repeated data loading and keep the processing pipeline more manageable in a local demonstration environment. 

However, these implementation choices do not establish a specific universal FPS. 

## **5.21 Academic and Research Benefits** 

N-ONE provides value as an academic project because it combines several areas of computer science in one implementation. 

The project can demonstrate practical concepts related to: 

- Artificial Intelligence 

- Computer Vision 

- Face Recognition 

- Image Processing 

- Python Programming 

- Streamlit Application Development 

- Role-Based Access Control 

- Data Management 

- Model Evaluation 

- Security Logging 

- Human-in-the-Loop Systems 

This makes the project suitable for demonstrating how theoretical concepts can be combined into a working application. 

## **5.22 Experimental Reproducibility** 

The evaluation workspace provides another important benefit: reproducibility. 

A benchmark can document: 

- Dataset 

- Enrollment/test separation 

- Model 

- Detector 

- Metric 

- Threshold 

- Test conditions 

- Calculated metrics 

- Performance measurements 

This makes it easier for another developer or evaluator to understand how a particular result was obtained. 

The benefit is particularly important in AI projects because simply reporting that “the model worked” does not provide enough information to reproduce the experiment. 

## **5.23 Transparent Limitations** 

Another benefit of the N-ONE design is that the project explicitly separates implemented features from experimentally established results. 

For example: 

##### **Implemented:** 

- Staff recognition 

- Unknown Re-ID 

- Threat heuristics 

does not automatically mean: 

##### **Quantitatively validated:** 

- Staff recognition accuracy 

- Unknown Re-ID accuracy 

- General threat-detection accuracy 

This distinction improves the technical credibility of the project documentation. 

## **5.24 Improved Project Maintainability** 

Predictable directories, structured CSV files, modular processing, and explicit configuration can make the project easier to maintain. 

A developer can more easily determine: 

- Where profiles are stored. 

- Where unknown observations are stored. 

- Where Victim sightings are stored. 

- Where evaluation data is stored. 

- Which configuration is being used. 

- Which component is responsible for a particular function. 

This reduces ambiguity during future development. 

## **5.25 Future Extensibility** 

The current architecture provides a foundation for future improvements. 

Potential future extensions include: 

- Database-backed storage 

- Improved face-recognition models 

- GPU acceleration 

- More advanced object detection 

- Better tracking algorithms 

- Multi-camera orchestration 

- Centralized alert management 

- Enterprise authentication 

- Encrypted data storage 

- Advanced audit infrastructure 

- Larger and more diverse evaluation datasets 

These should be treated as **future scope** , not as current project capabilities unless implemented and verified. 

## **5.26 Security and Access-Control Benefits** 

The authentication and role-separation mechanisms provide a basic access-control benefit. Administrator controls are separated from Operator workflows. 

This reduces the possibility that every user can directly access sensitive management operations. 

The application also includes: 

- Secret-based configuration 

- Constant-time credential comparison 

- Failed-login lockout 

- Logout 

- Administrator-only destructive operations 

These mechanisms improve the security posture of the prototype. 

However, they do not establish a complete production security architecture. 

## **5.27 Privacy-Oriented Benefits** 

The controlled registration workflow and local data organization provide some privacy-oriented design benefits. 

For example, the system stores a focused face crop for recognition rather than requiring the full original registration image to be used as the recognition reference. 

Role separation also restricts who can access administrative functionality. 

However, these design choices should not be presented as proof of legal or regulatory compliance. 

A real deployment would require additional controls for: 

- Data retention 

- Data deletion 

- Access auditing 

- Encryption 

- Privacy governance 

- Applicable legal requirements 

## **5.28 Benefit of Evidence-Based Development** 

A major engineering advantage of N-ONE is the attempt to distinguish between assumptions and measurements. 

Instead of saying: 

“Model X is always the best.” 

the evaluation process asks: 

“How did each tested configuration behave under the defined dataset, threshold, and hardware conditions?” 

This makes the project more scientifically defensible. 

Similarly, instead of saying: 

“The system works perfectly in real time.” 

the report can document actual measured latency and explain the conditions under which it was measured. 

## **5.29 Benefit of Separating Capability From Guarantee** 

The project architecture encourages a distinction between: 

#### **Capability** 

What the software has been implemented to do. 

#### **Measurement** 

What the evaluation has experimentally demonstrated. 

#### **Guarantee** 

What can be expected under all possible real-world conditions. 

For example: 

**Capability:** Victim Search is implemented. 

**Measurement:** A defined benchmark can measure its behavior. 

**Guarantee:** Universal Victim recognition accuracy is not established. 

This distinction is particularly important for AI-based systems. 

## **5.30 Overall Benefits Summary** 

The major benefits of N-ONE can be summarized in the following table: 

|**Benefit**|**Description**|
|---|---|
|Integrated workflow|Combines registration, monitoring, recognition, logging, and<br>review|
|Controlled enrollment|Requires one visible face during registration|
|Focused profile data|Stores padded face crops for registered subjects|
|Target-restricted<br>search|Keeps Victim Search tied to the selected target|
|Unknown context|Maintains local repeat-unknown observations|
|Location awareness|Associates sightings with camera/location information|



|Auditability|Maintains reviewable CSV-based records|
|---|---|
|Model evaluation|Allows multiple recognition configurations to be tested|
|Threshold analysis|Studies recognition behavior at different decision boundaries|
|Quantitative evidence|Provides TP/TN/FP/FN and derived metrics|
|Human oversight|Keeps important decisions with an authorized operator|
|Modular design|Separates recognition, threat, logging, and dashboard functions|
|Local deployment|Suitable for controlled academic/laboratory environments|
|Research value|Supports study of AI, CV, recognition, security, and evaluation|
|Future extensibility|Provides a foundation for additional models and infrastructure|



## **5.31 Important Conditions and Limitations of the Benefits** 

The benefits described above are **conditional on the project's implementation and operating environment** . 

They do not establish: 

- Universal face-recognition accuracy. 

- Guaranteed Victim discovery. 

- Guaranteed threat detection. 

- Universal real-time FPS. 

- Enterprise-scale camera capacity. 

- Complete Staff recognition accuracy. 

- Quantitatively validated Unknown Re-ID accuracy. 

- Complete legal compliance. 

- Complete biometric-data protection. 

- Error-free autonomous surveillance. 

The actual behavior of the system depends on factors including: 

- Input quality 

- Enrollment quality 

- Lighting 

- Pose 

- Occlusion 

- Camera distance 

- Recognition model 

- Detector 

- Threshold 

- Hardware 

- Dataset composition 

- Operating environment 

Therefore, all performance-related claims should be connected to the specific experimental conditions under which they were measured. 

## **5.32 Role of the Human Operator** 

The human operator remains an essential part of the N-ONE workflow. 

The operator is responsible for interpreting system results in context. 

For example, a recognition result should be reviewed using available: 

- Image evidence 

- Camera information 

- Timestamp 

- Recognition distance 

- Sighting history 

- Operational context 

Similarly, a threat heuristic should be reviewed before treating it as an actual threat. 

The system therefore follows the principle: 

##### **AI provides assistance; the authorized human operator provides contextual judgment.** 

This approach is particularly important when false positives or false negatives could affect subsequent decisions. 

## **5.33 Final Benefit Statement** 

The overall benefit of N-ONE is the creation of an **integrated, evidence-oriented AI-assisted surveillance workflow** rather than simply a face-recognition demonstration. 

The system connects: 

##### **Controlled Registration** 

↓ 

##### **Target Selection** 

↓ 

##### **Visual Monitoring** 

↓ 

##### **Face/Threat Analysis** 

↓ 

##### **Recognition or Alert** 

↓ 

##### **Location and Timestamp Context** 

↓ 

##### **Structured Logging** 

↓ 

##### **Human Review** 

↓ 

##### **Experimental Evaluation** 

This integration makes N-ONE useful as an academic prototype and research-oriented evaluation platform. 

Its strongest benefits are therefore not claims of perfect recognition or autonomous surveillance, but the combination of **controlled workflows, target-specific processing, repeat-observation context, predictable local data handling, measurable recognition evaluation, and reviewable evidence** . 

At the same time, the project maintains an important boundary: these benefits do not establish universal recognition accuracy, guaranteed threat classification, measured application-wide FPS, production-scale deployment, or legal compliance. Those claims would require additional datasets, testing, infrastructure, governance, and independent validation. 

Thus, N-ONE should be understood as a **human-supervised AI-assisted surveillance prototype whose value lies in integrating operational workflows and making their results measurable, traceable, and reviewable** . 

## **CHAPTER 6 – MAIN MODULES** 

N-ONE is organized into several functional modules that work together to provide authentication, profile management, camera ingestion, face recognition, Victim Search, unknown-person reidentification, threat monitoring, and audit-oriented logging. Each module has a defined responsibility so that recognition, threat analysis, and administrative operations remain separated. 

### **6.1 Authentication and RBAC** 

The authentication module controls access to the N-ONE dashboard. The function load_auth_credentials() reads the configured administrator and operator credentials from either the process environment or Streamlit Secrets. 

The system expects the following configuration values: 

- ADMIN_USERNAME 

- ADMIN_PASSWORD 

- OPERATOR_USERNAME 

- OPERATOR_PASSWORD 

If any required credential is missing, the application raises an error and the dashboard does not proceed normally. 

After successful authentication, the application stores the authentication state and selected role in Streamlit session state. This role determines which functions are available to the user. 

The **Administrator** role can access functions such as: 

- Staff and Victim registration 

- Model configuration 

- Profile management 

- Deletion or reset-related controls 

The **Operator** role is intended for operational activities such as: 

- Monitoring camera sources 

- Running recognition/search operations 

- Reviewing results and logs 

This separation reduces the possibility of normal operators modifying configuration or performing destructive administrative operations. 

### **6.2 Profile Registration** 

The profile-registration module is used by an Administrator to create Staff or Victim profiles. 

The system supports two registration approaches: 

1. **Guided multi-angle capture** 

2. **Image upload** 

Guided capture expects images from multiple directions: 

- Front 

- Left 

- Right 

- Up 

- Down 

Each submitted image is decoded and processed for face detection. The registration process requires exactly one detectable face and a minimum acceptable face size. This prevents ambiguous images containing multiple people from being directly used as profile references. 

After validation, the system creates a padded face crop. The current implementation uses approximately **25% padding** around the detected face region before saving the profile image. 

Profiles are stored using generated identifiers corresponding to their role, such as: 

Staff_<profile_id>.jpg Victim_<profile_id>.jpg 

When an existing profile is updated, the relevant angle images associated with that profile ID are replaced. 

This registration workflow provides a more controlled reference set for subsequent recognition operations. 

### **6.3 Camera Ingestion** 

The camera-ingestion module provides different ways of supplying visual data to N-ONE. 

#### **Browser Camera** 

The application can optionally use WebRTC for browser-based camera capture. This is particularly useful when N-ONE is accessed remotely because the server process normally cannot directly access the physical camera attached to a user's computer. 

#### **Local Webcam** 

For locally connected cameras, the application uses OpenCV and can probe multiple camera indices and Windows-specific camera backends to locate an available device. 

#### **Recorded Video** 

Uploaded video files are temporarily written as: 

temp_video_upload.mp4 

The application can then process the recorded video through its recognition or monitoring pipeline. 

#### **IP Camera** 

An IP camera source can be supplied as a camera URL and passed to OpenCV for processing. 

Therefore, the camera layer supports browser-based capture, local cameras, recorded videos, and IP camera sources, subject to the runtime environment and available dependencies. 

### **6.4 Face Recognition and Matching** 

The face-recognition module performs detection, representation, and matching of faces against the application's known profile cache. 

The active DeepFace-compatible recognition object provides detected face regions and corresponding embeddings. The application first searches the known-profile cache for potential matches. 

The candidate set depends on the operational mode. 

In **Victim Search** , matching is restricted to the selected Victim profile. This means the application does not intentionally treat every registered Staff or Victim profile as a candidate for the selected search. 

In **attendance/normal recognition** , the known profiles can be considered as candidates for recognition. 

When a face does not match a known profile, the system proceeds to the unknown-person workflow. The detected face is compared with the stored unknown-person records to determine whether it represents a previously observed unknown individual. 

This creates the following general flow: 

Camera Frame ↓ Face Detection ↓ Face Representation ↓ Known Profile Matching ↓ Match Found? ── Yes → Known Identity Result │ No ↓ Unknown Cache Matching ↓ Existing Unknown? ↙       ↘ Yes        No ↓          ↓ Update     Create Record     Unknown ID 

The exact recognition behavior depends on the active backend and operational mode. 

### **6.5 Unknown Re-ID** 

The Unknown Re-ID module provides local tracking of people who cannot be matched with a registered profile. 

When a new unknown person is detected, the system assigns an identifier such as: 

unknown_001 unknown_002 unknown_003 

The associated face crop is saved, while metadata about the first and latest observation is maintained in: 

unknown_person_db.csv 

Individual sightings are also recorded in the unknown-sighting log. 

When the same unknown face is observed again and successfully matches the stored unknown representation, the system updates information such as: 

- Last-known location 

- Last observation timestamp 

- Sighting information 

The system also writes another sighting record, subject to the implemented **two-second write throttle** for the same unknown ID and camera location. 

It is important to distinguish this function from real-world identity recognition. An identifier such as unknown_001 represents a locally re-identified observation, not the actual name or identity of the person. 

### **6.6 Victim Search** 

Victim Search is one of the primary operational modules of N-ONE. 

Before starting the search, the operator selects a registered Victim profile and enters the camera location. The recognition process then operates with the selected Victim as the target. 

When the target is successfully matched, N-ONE creates a **Victim Found** event. 

The result card provides information including: 

- Victim profile image 

- Profile ID 

- Camera location 

- Recognition distance 

- Timestamp 

- Active model 

- Recognition backend 

- Distance metric 

- Latest sighting for each recorded location 

This provides an operator-oriented view of where and when the selected target was detected. 

The system also has a defined boundary for the OpenCV fallback. When the fallback backend is being used, visible identity matching is disabled. In that situation, the interface can confirm that a face was detected but does not label that face as a specific Victim. 

This distinction prevents the fallback detector from being represented as a full identity-recognition system. 

### **6.7 Threat Detection** 

Threat Detection operates as a separate processing path from face recognition. 

The threat-detection mode does **not** use: 

- FaceNet 

- FaceNet512 

- ArcFace 

- Face-recognition cosine threshold 

Instead, the implemented heuristic path uses image-processing techniques including: 

- Canny edge detection 

- Morphological processing 

- Contour geometry 

- Warm-colour HSV masking 

These techniques are used to identify visual patterns that may correspond to possible threats or firelike regions. 

Detected alerts are throttled before being written to the audit records to avoid excessive repeated logging. 

The resulting event is intentionally represented as: 

##### **Possible threat/fire** 

rather than a verified weapon or fire classification. 

Therefore, the output should be treated as an alert requiring operator review rather than as a definitive classification. 

### **6.8 Dashboard and Logs** 

The dashboard provides a centralized interface for viewing the current state of the system. 

Authenticated users can see information such as: 

- Current user role 

- Number of registered profiles 

- Number of unknown persons 

- Total log events 

The registered-profile inventory can be filtered by: 

- All 

- Staff 

- Victim 

Users with appropriate access can inspect profile photographs and associated metadata. The dashboard also provides access to unknown-person records and Victim sighting history. 

The logging system provides persistent records that can be reviewed after an operational session. This makes the system suitable not only for live monitoring but also for reviewing recorded events and evaluating system behavior. 

### **Table 4 – Project Modules** 

|**Module**|**Status**|**Main Output**|
|---|---|---|
|Authentication/<br>RBAC|Implemented|Role-gated session|
|Registration|Implemented|Face-only profile<br>images|
|Victim Search|Implemented with runtime dependency<br>boundary|Target result or no-<br>match|
|Staff/Attendance|Implemented workflow; Staff benchmark<br>unavailable|Known/unknown<br>status|
|Unknown Re-ID|Implemented local storage workflow;<br>accuracy unavailable|Unknown ID/history|
|Threat Detection|Implemented heuristic path|Possible threat/fire<br>alert|
|WebRTC Camera|Optional/conditional|Worker-thread<br>annotation|
|Evaluation|Implemented evidence workspace|CSV metrics|



New Neural Training Not implemented 

None 

#### **6.9 Module Integration** 

The modules operate as a connected workflow rather than as completely independent features. Authentication determines the user's permissions, registration creates the reference profiles, camera ingestion supplies visual data, and the recognition or threat-processing pipeline analyzes that data according to the selected operational mode. 

The resulting events are then presented through the dashboard and stored in the relevant logs. 

The overall module flow can therefore be represented as: 

Authentication / RBAC 

↓ Dashboard ↓ ┌────────┼───────────┐ ↓        ↓           ↓ Register  Camera      Evaluation Profiles  Ingestion   Workspace ↓ 

Processing Mode 

↓ ┌────────┼──────────────┐ ↓        ↓              ↓ Victim   Staff /        Threat Search   Attendance     Detection ↓        ↓              ↓ Known / Unknown Results / Alerts ↓ 

Logging & Review 

This modular structure allows N-ONE to keep identity recognition, unknown-person handling, threat analysis, and administrative operations logically separated while still providing a unified operator workflow. 



<!-- Start of picture text -->
N-ONE SYSTEM ARCHITECTURE<br>(MODULE INTEGRATION AND DATA FLOW)<br>1, AUTHENTICATION AND RBAC 2. DASHBOARD (MAIN INTERFACE) 3. PROFILE REGISTRATION<br>° Op Marinate fee Guest Argtecone mae Ua<br>‘Admin2 veerameOperatora Login Lp] ++tle$MecormemenmrtalDeletioncon raten contlsr g etin Hp 2 =nee BR= = 8 3mee” Bi= retgeraeut my +oe ] FemUp image<br>:. o Q wy Face Detection<br>Sire © Operator en,es IRR, WetSeech sa tetnce oe<br>z Cee 25xPadeFace Cop<br>Se ae TreatA Detection Viewinvenirya Vw] Logs haonal (StaffSetaD>jpg Veten Pis10> jpn)<br>‘4. CAMERA INGESTION: 5. PROCESSING MODULES [6 UNKNOWN REID | 8, OUTPUT AND REVIEW<br>5 agecognon 22 vermacncr (59 maroc | | ronan emt CO ess<br>Caetw mg [pn“Tone (opeFace Repesertatin Opn)5 Tat dlsee+ ahig Morphology=7 tii ==baer? Bopp<br>coevanminesFloato epics= ownUrkeown rfl Matching+" Mating emaesoutFrca aar a 7+ 5 sg {urtnown,StanOOF kno,C 0 2,.) Proneote‘etyand eseen<br>(UR) own / known Rest eterna ee teste Up wninon psn do<br>‘dean alton Rete<br>J W—_— + scandal al corereer<br>s aa Pe aa7. DATAY STORAGE (LOCAL FILESf-AND CSV SsLOGS) eZ 2 2@e Human Review<br>RegisteredGatesProfiles,| |‘Unknowneirom Profileseo _unknown_sightingscommu log.csy_"| | “tweenvietim_sightingszs log.csv_eta oeauditTe log.cov cy osficationard Action) |<br>Figure 6.1. Overall Architecture and Module Integration of N-ONE.<br><!-- End of picture text -->

## **CHAPTER 7 – TECHNICAL OVERVIEW** 

N-ONE is implemented as a Python-based computer-vision application with a Streamlit dashboard. Its technical architecture combines image processing, face detection, optional neural face representation, vector comparison, CSV-based persistence, and browser-based camera support. The system is designed so that the core application can operate with an OpenCV-based fallback while the full neural face-analysis path is available when its runtime dependencies are present. 

The technical design can therefore be understood as two major processing paths: 

1. **Face recognition and identity-processing path** 

2. **Independent threat-detection path** 

The threat-detection path is intentionally separate from the face-recognition models and should not be interpreted as a weapon-recognition function of FaceNet, FaceNet512, or ArcFace. 

### **7.1 Technology Stack** 

The following technologies form the primary technical stack of N-ONE. 

**Technology** 

##### **Confirmed Role** 

**Python** Main application and processing language 

|**Streamlit 1.60.0**|Dashboard interface and session-state management|
|---|---|
|**OpenCV**|Image/video processing, Haar detection, contours, annotations|
|**NumPy**|Numerical arrays, vector operations, and distance calculations|
|**pandas**|CSV persistence and tabular data display|
|**Pillow**|Uploaded-image decoding and image manipulation|
|**DeepFace 0.0.100**|Conditional neural face-analysis interface|
|**TensorFlow**|Conditional dependency for the full neural runtime|
|**streamlit-webrtc**<br>**0.77.0**|Optional browser-camera processing on supported Python<br>versions|
|**PyAV**|Optional WebRTC frame conversion|



#### **Python** 

Python acts as the primary programming language of N-ONE. It connects the user interface, imageprocessing pipeline, recognition adapters, logging system, evaluation components, and storage mechanisms. 

Python is particularly suitable for this project because the application depends on computer-vision and numerical-processing libraries such as OpenCV, NumPy, pandas, and the optional DeepFace/TensorFlow stack. 

#### **Streamlit** 

Streamlit provides the main web-based dashboard. 

It is responsible for: 

- Login interface 

- Role-based dashboard 

- Profile registration 

- Camera controls 

- Victim Search 

- Staff/attendance workflow 

- Threat Detection interface 

- Inventory display 

- Log review 

- Evaluation interface 

- Session-state management 

The application therefore does not require a separate traditional frontend framework for its main dashboard. 

Streamlit session state is also used to preserve important runtime information such as authentication status, selected role, selected operational mode, selected Victim, camera location, and latest results. 

#### **OpenCV** 

OpenCV forms an important part of the application's computer-vision layer. 

Its confirmed responsibilities include: 

- Image decoding 

- Video-frame processing 

- Haar-cascade face detection 

- Grayscale conversion 

- Image enhancement 

- Contour processing 

- Edge detection 

- Morphological operations 

- HSV-based colour analysis 

- Bounding-box annotation 

- Camera access 

OpenCV is also important because it provides the fallback recognition representation when the full neural runtime is unavailable. 

#### **NumPy** 

NumPy provides the numerical array infrastructure required for image and feature processing. 

Within N-ONE it supports operations such as: 

- Image arrays 

- Face crops 

- Feature vectors 

- Vector normalization 

- Distance calculations 

- Numerical comparisons 

Face embeddings or fallback descriptors are represented as numerical vectors, allowing mathematical comparison between a stored profile and a detected face. 

#### **pandas** 

pandas is used primarily for structured data handling and CSV-based persistence. 

Examples include: 

unknown_person_db.csv 

unknown_sighting_log.csv 

victim_sighting_log.csv 

pandas also supports the dashboard's tabular presentation of records and the evaluation workspace's metric tables. 

This makes the project's stored results relatively easy to inspect and analyze using standard dataanalysis tools. 

#### **Pillow** 

Pillow is used for uploaded-image decoding and image manipulation. 

It provides an additional image-processing interface around uploaded files before they enter the face-processing pipeline. 

#### **DeepFace and TensorFlow** 

DeepFace provides the conditional neural face-analysis interface used by N-ONE when the complete neural runtime is available. 

TensorFlow is a conditional dependency for this full neural path. 

The important architectural point is that **DeepFace/TensorFlow are not the only processing path in N-ONE** . The application contains a fallback OpenCV-based backend so that the application architecture can remain functional when the complete neural environment is unavailable. 

#### **WebRTC and PyAV** 

streamlit-webrtc provides the optional browser-camera processing path on supported Python environments. 

This is useful for remote deployments because the browser can provide camera frames to the application rather than requiring the server to directly access the user's physical webcam. 

PyAV is used as the optional frame-conversion component associated with this WebRTC path. 

## **7.2 DeepFace and Model Roles** 

The neural face-analysis architecture contains multiple models with different responsibilities. They should not be treated as interchangeable components. 

The primary representation models considered by N-ONE include: 

- **FaceNet** 

- **FaceNet512** 

- **ArcFace** 

These models are used to generate face representations that can subsequently be compared using a distance metric. 

#### **FaceNet** 

FaceNet is used as a face-representation model. A detected face is converted into a numerical representation, commonly referred to as an embedding. 

Conceptually: 

Face Image 

↓ 

Face Detection 

↓ 

FaceNet 

↓ 

Numerical Face Representation 

↓ 

Distance Comparison 

The representation itself is not a person's name. Identity is determined by comparing the representation with stored reference representations. 

#### **FaceNet512** 

FaceNet512 is another representation model available through the neural face-analysis interface. It follows the same general conceptual process: 

Input Face 

↓ 

Preprocessing 

↓ 

FaceNet512 

↓ 

Embedding 

↓ 

Cosine Distance 

↓ 

Threshold Decision 

The use of FaceNet512 does not automatically mean that it will produce better results in every environment. Model performance depends on the dataset, detector, threshold, image quality, pose, lighting, and deployment conditions. 

#### **ArcFace** 

ArcFace is also used as a face-representation model. 

Its role is to produce a representation that can be compared with stored representations of enrolled subjects. 

The N-ONE evaluation workspace can therefore compare different representation models under controlled benchmark conditions rather than assuming that one model is universally superior. 

#### **RetinaFace** 

RetinaFace has a different role. 

It is primarily a **face detector** , not an identity representation model. 

Its purpose is to locate faces within an image so that the detected region can subsequently be passed through a recognition/representation process. 

The distinction can be represented as: 

Face Processing 

│ ┌────────────┴────────────┐ ↓                         ↓ 

Face Detection             Face Representation ↓                         ↓ 

RetinaFace              FaceNet / FaceNet512 

/ ArcFace 

Therefore, RetinaFace should not be described as an identity-recognition model in the project report. 

#### **OpenCV as Default Detector** 

The application's source/default detection path uses OpenCV-based detection. 

This is separate from the RetinaFace detector used in the conditional neural evaluation path. 

Consequently, detector and representation choices must be recorded separately when discussing benchmark results. 

## **7.3 Face Recognition Processing Pipeline** 

The general neural recognition pipeline can be represented as follows: 

Camera / Image 

↓ 

Frame Acquisition 

↓ 

Face Detection 

↓ 

Face Region Extraction 

↓ 

Preprocessing ↓ 

Face Representation Model 

↓ 

Embedding / Feature Vector ↓ 

Known Profile Comparison 

↓ 

Cosine Distance 

↓ 

Threshold Evaluation 

↓ 

Match / No Match 

If no registered profile satisfies the matching condition, the system can proceed to its unknownperson processing path. 

For Victim Search, the candidate set is further restricted to the selected Victim profile. 

## **7.4 Cosine Distance** 

N-ONE uses cosine distance for comparing face representations in the relevant recognition configuration. 

For two vectors aa and bb, cosine distance can be represented as: 

dcos(a,b)≠1−⋅∥∥∥∥a b a b d_{cos}(a,b) ≠ 1- \frac{a\cdot b} {\|a\|\|b\|} 

where: 

- aa = first face representation 

- bb = second face representation 

- ⋅ 

- a ba\cdot b ≠ dot product 

- ∥∥a \|a\| ≠ magnitude of vector aa 

- ∥∥b \|b\| ≠ magnitude of vector bb 

The resulting distance represents the difference between the two representations. 

#### **Interpretation** 

N-ONE treats: 

- **Lower distance → greater similarity** 

- **Higher distance → lower similarity** 

A match is accepted when: 

dcos≤τd_{cos} \leq \tau 

where τ\tau represents the configured recognition threshold. 

The current default threshold is: 

##### 0.40 

However, this value should not be interpreted as a universal face-recognition threshold. The appropriate threshold depends on the representation model, detector, preprocessing configuration, dataset, and operational conditions. 

## **7.5 Threshold-Based Matching** 

The threshold provides the decision boundary between a potential match and a non-match. 

For example: 

Detected Face 

↓ 

Generate embedding 

↓ 

Compare with reference 

↓ 

Calculate cosine distance 

↓ 

d ≤ 0.40 ? /          \ Yes           No ↓             ↓ 

Potential       No Match 

Match 

A threshold that is too strict may reject genuine appearances of the enrolled person. This contributes to false negatives. 

A threshold that is too permissive may allow visually similar but incorrect people to be accepted. This can increase false positives. 

Therefore, threshold selection is an evaluation problem rather than simply a fixed mathematical constant. 

## **7.6 OpenCVFaceBackend – Fallback Representation** 

N-ONE also contains an OpenCVFaceBackend that provides a lightweight fallback when the full neural face-recognition runtime is unavailable. 

This backend should **not** be described as a pretrained neural identity-recognition network. 

Its processing pipeline uses traditional computer-vision techniques. 

The fallback includes: 

- Frontal Haar cascades 

- Profile Haar cascades 

- Equalized grayscale 

- Optional image upscaling 

- Overlapping detection-box deduplication 

- Face cropping 

- CLAHE enhancement 

- HOG feature extraction 

- Feature-vector normalization 

The simplified processing sequence is: 

Input Image 

↓ 

Haar Face Detection 

↓ 

Frontal/Profile Detection 

↓ 

Overlapping Box Deduplication 

↓ 

Face Crop 

↓ 

64 × 64 Grayscale Representation ↓ 

CLAHE Enhancement 

↓ 

HOG Descriptor 

↓ 

Vector Normalization 

↓ 

Feature Representation 

#### **64 × 64 Representation** 

The detected face region is converted into a standardized **64 × 64 grayscale representation** before the feature-extraction process. 

Standardizing the input size provides a consistent representation for subsequent feature calculation. 

#### **CLAHE** 

Contrast Limited Adaptive Histogram Equalization (CLAHE) is applied to improve local contrast in the grayscale face representation. 

This can help make local structural information more consistent under some lighting conditions, although it does not eliminate recognition problems caused by severe illumination changes or poor image quality. 

#### **HOG** 

Histogram of Oriented Gradients (HOG) is used to describe local gradient and edge structures within the face crop. 

The resulting descriptor is normalized and used as the fallback representation. 

The important distinction is that this representation is based on engineered computer-vision features rather than a learned deep neural face-embedding model. 

## **7.7 Neural Runtime and Fallback Architecture** 

The N-ONE architecture can therefore be viewed as having two recognition-runtime conditions. 

#### **Full neural runtime** 

Camera/Image 

↓ 

Face Detection 

↓ 

DeepFace-compatible processing ↓ 

FaceNet / FaceNet512 / ArcFace 

↓ 

Embedding 

↓ 

Cosine Distance 

↓ 

Threshold ↓ 

Identity Decision 

#### **OpenCV fallback** 

Camera/Image 

↓ 

OpenCV Face Detection ↓ 

Face Crop ↓ Grayscale + CLAHE ↓ 

HOG Descriptor 

↓ 

Normalized Feature Vector ↓ 

Comparison 

This runtime boundary is important when interpreting experimental results. 

A benchmark performed with a neural representation model and a particular detector should not automatically be described as the exact performance of the OpenCV fallback or the complete production application. 

## **7.8 Implemented and Conditional Features** 

The N-ONE interface contains hooks and adapter surfaces for several face-analysis capabilities. 

These include functions related to: 

- Face attributes 

- Face extraction 

- One-to-one verification 

- Anti-spoofing/liveness-related operations 

However, the presence of a UI hook or adapter does not by itself prove that the corresponding neural capability is active in every runtime environment. 

The actual availability depends on the backend and dependencies loaded during execution. 

The audited OpenCV fallback implements the core representation, finding, and verification adapter surface, but it does **not** establish that all neural attribute-analysis or liveness/anti-spoofing operations are active. 

Therefore, the report distinguishes between: 

|**Capability**|**Status/Interpretation**|
|---|---|
|Face detection|Implemented|
|Face representation|Neural path conditional; OpenCV fallback available|
|Face finding/matching|Implemented through backend architecture|
|One-to-one verification<br>interface|Available through adapter surface|
|Face attributes|Conditional; not established as active in fallback|
|Anti-spoofing/liveness|Conditional; active availability not established in audited<br>fallback|
|Threat detection|Separate OpenCV heuristic path|



This distinction is important for technical accuracy and prevents interface-level functionality from being incorrectly presented as fully active AI capability. 

## **7.9 Separation of Face Recognition and Threat Detection** 

A major architectural principle of N-ONE is the separation between identity recognition and threat analysis. 

The face-recognition path uses face representations and distance comparison. 

The threat path instead uses image-processing operations such as: 

Frame 

↓ 

Canny Edge Detection 

↓ 

Morphological Processing 

↓ 

Contour Analysis 

↓ 

Warm HSV Mask 

↓ 

Heuristic Evaluation 

↓ 

Possible Threat / Fire Alert 

Therefore: 

##### **FaceNet, FaceNet512, and ArcFace are not being used as weapon-detection models in N-ONE.** 

Similarly, a threat alert should not automatically be interpreted as a verified weapon or fire classification. It is a heuristic indication that requires human review. 

## **7.10 Technical Data Flow** 

The major technical components can be summarized through the following data flow: 

N-ONE INPUT │ ┌────────────────┼────────────────┐ ↓                ↓                ↓ Browser Camera    Local Camera     Video/IP Source │                │                │ └────────────────┼────────────────┘ ↓ Frame Processing │ ┌───────────┴───────────┐ ↓                       ↓ Face Processing         Threat Processing │                       │ Face Detection          Canny / HSV ↓                 / Contours Representation               ↓ ↓                Possible Alert Vector Comparison ↓ Known / Unknown Result │ ┌──────┴──────┐ ↓             ↓ Known          Unknown │             │ 

↓             ↓ 

Victim/Staff     Unknown Re-ID 

│             │ └──────┬──────┘ ↓ 

CSV / Local Logs 

↓ 

Dashboard Review 

This architecture allows N-ONE to process multiple types of visual input while keeping identity recognition, unknown re-identification, and threat analysis logically separated. 

### **7.11 Technical Limitations** 

The technical architecture also introduces several limitations that should be considered when interpreting system performance. 

First, the neural recognition path depends on the required runtime dependencies being available. If the complete neural environment is unavailable, the application may operate through the OpenCV fallback, which has different recognition characteristics. 

Second, the recognition threshold is not universal. A value such as 0.40 represents a configuration choice that should be evaluated against the selected model, detector, and dataset. 

Third, face recognition quality is influenced by the input conditions. Factors such as: 

- Lighting 

- Pose 

- Blur 

- Occlusion 

- Camera distance 

- Face size 

- Detection quality 

can influence the resulting representation and matching decision. 

Finally, the presence of conditional UI interfaces for advanced capabilities does not establish that those capabilities are active in every deployment. 

### **7.12 Technical Overview Summary** 

The N-ONE technical architecture combines a Python/Streamlit application layer with OpenCVbased computer vision, optional DeepFace/TensorFlow neural face processing, NumPy-based numerical computation, pandas-based CSV persistence, and optional WebRTC camera ingestion. 

The face-recognition system distinguishes between **detection** , **representation** , and **matching** . FaceNet, FaceNet512, and ArcFace serve as representation models, while RetinaFace is a detector. The system uses cosine distance to compare representations and applies a configurable threshold to make matching decisions. 

At the same time, OpenCVFaceBackend provides a lightweight fallback based on Haar detection, grayscale preprocessing, CLAHE, HOG descriptors, and vector normalization. This fallback should not be represented as equivalent to the neural recognition models. 

Threat Detection remains a separate heuristic computer-vision path based on edges, morphology, contours, and HSV analysis. This separation is essential for accurately describing what N-ONE actually implements and for avoiding unsupported claims about AI-based weapon classification or universal face-recognition performance. 

## **CHAPTER 8 – SYSTEM CONFIGURATION** 

System configuration defines the software environment, hardware considerations, camera and network requirements, and operational parameters required for running N-ONE. Since the project supports both an OpenCV fallback path and an optional neural face-analysis path, the exact environment depends on which processing mode is being used. 

The configuration described in this chapter is based on the current project implementation and the audited evaluation environment. Where the repository does not provide measured information, the value is explicitly identified as unavailable rather than being estimated. 

### **8.1 Software Configuration** 

N-ONE is developed primarily using Python and targets **Python 3.10 or later** for the base application. 

The project supports an OpenCV-based fallback environment that can operate on newer Python versions, while the optional neural face-analysis environment has more restrictive compatibility considerations because TensorFlow availability depends on the Python version and operating environment. 

#### **Base software environment** 

The main software components include: 

- Python 3.10+ 

- Streamlit 

- OpenCV 

- NumPy 

- pandas 

- Pillow 

- Optional WebRTC components 

- Optional DeepFace/TensorFlow environment 

The OpenCV fallback is particularly important because it provides a processing path when the complete neural runtime is not available. 

#### **Neural evaluation environment** 

The audited benchmark environment used: 

Operating System : Windows 11 Python           : 3.12.10 DeepFace         : 0.0.101 TensorFlow       : 2.21.0 OpenCV           : 4.11.0 NumPy            : 2.5.3 

The benchmark environment was configured for CPU execution. GPU acceleration was not measured during the reported benchmark. 

This environment should be distinguished from the application's general runtime because the benchmark specifically tested the neural face-recognition models under a separate controlled environment. 

#### **Python compatibility** 

The project requirements target Python 3.10+, while the optional neural environment is more dependent on the availability of compatible TensorFlow packages. 

Therefore, the practical environment can be represented as: 

N-ONE Application │ ├── Base Runtime │      └── Python 3.10+ │ └── Optional Neural Runtime ├── Compatible Python version ├── DeepFace └── TensorFlow 

This separation is important because installing the base application does not necessarily guarantee that the complete neural recognition stack will be available. 

### **8.2 Hardware Configuration** 

The current repository does not define a measured minimum hardware configuration for N-ONE. 

Although the benchmark environment provides processor information, it does not provide a complete deployment specification containing all of the following: 

- Exact minimum CPU requirement 

- Minimum RAM requirement 

- Required GPU 

- Minimum GPU VRAM 

- Guaranteed application FPS 

- Maximum supported camera count 

Therefore, this report does **not** claim a specific minimum CPU, RAM, GPU, FPS, or camera capacity. 

#### **Benchmark hardware limitation** 

The benchmark documentation indicates that CPU execution was requested. However, RAM availability was not recorded and GPU performance was not measured. 

Consequently, the benchmark results should not be interpreted as a complete hardware-performance characterization. 

For example, the project should not claim: 

“N-ONE requires 8 GB RAM and achieves 30 FPS.” 

unless those values are actually measured on the demonstration system. 

#### **Recommended final demonstration documentation** 

For the final university submission, the actual machine used for the project demonstration should be documented. 

The following information can be added: 

|**Hardware Parameter**|**Demonstration Machine**|
|---|---|
|Processor|Actual CPU model|
|RAM|Actual installed RAM|
|GPU|Actual GPU, if present|
|GPU VRAM|Actual VRAM, if applicable|
|Operating System|Actual OS|
|Camera|Actual camera model/type|
|Storage|Actual storage configuration|
|Python|Installed Python version|



This provides reproducibility without inventing hardware requirements. 

### **8.3 Network and Camera Configuration** 

N-ONE supports multiple camera-input approaches, and each approach has different environmental requirements. 

#### **Browser Camera** 

The browser-camera path uses WebRTC and requires: 

- A supported web browser 

- Camera permission 

- Working browser access to the camera 

- Compatible WebRTC dependencies 

- A running N-ONE application 

The browser requests permission to access the local camera and provides frames through the WebRTC processing path. 

The general flow is: 

Local Camera ↓ Web Browser ↓ Camera Permission ↓ WebRTC ↓ N-ONE Application ↓ Frame Processing 

This approach is particularly useful for remote deployment because the server does not need direct operating-system access to the user's physical webcam. 

#### **Local Webcam** 

A locally connected webcam can be accessed through OpenCV. 

The application can probe available camera indices and Windows camera backends to locate an accessible device. 

The basic flow is: 

USB / Built-in Webcam 

↓ 

Operating System 

↓ 

OpenCV ↓ N-ONE ↓ 

Frame Processing 

This method is most appropriate when the N-ONE application is running on the same machine that has physical access to the webcam. 

#### **Recorded Video** 

Recorded videos can be uploaded and temporarily stored as: 

temp_video_upload.mp4 

The video can then be processed through the application's visual-processing pipeline. 

This method is useful for controlled testing and evaluation because the same recorded footage can be processed repeatedly. 

#### **IP Camera** 

N-ONE can also accept an IP-camera stream through an OpenCV-compatible URL. 

Conceptually: 

IP Camera ↓ Network Stream ↓ OpenCV ↓ 

N-ONE Processing 

Actual performance depends on the network connection, stream format, camera configuration, resolution, and processing hardware. 

For security reasons, **real RTSP credentials, passwords, authentication tokens, or private camera URLs should not be included in the university report** . 

The report should instead use a sanitized representation such as: 

rtsp://<camera-host>/<stream> 

### **8.4 Recognition and Processing Configuration** 

The main recognition configuration controls the representation model, detector, distance metric, and matching threshold. 

The current default configuration is: 

Model      = Facenet Detector   = opencv Metric     = cosine Threshold  = 0.40 

These parameters are related to the face-recognition path and should not be confused with the separate Threat Detection configuration. 

#### **Recognition model** 

The current source default is: 

Facenet 

Other representation models such as FaceNet512 and ArcFace can be used in the neural evaluation environment. 

#### **Detector** 

The current source default is: 

opencv 

The OpenCV detector therefore represents the normal source configuration, while other detectors such as RetinaFace can be used in the appropriate neural benchmark environment. 

#### **Distance metric** 

The current default metric is: 

cosine 

The system compares face representations using cosine distance, where lower distance indicates greater similarity. 

#### **Threshold** 

The current default threshold is: 

0.40 

This value is a configuration parameter rather than a universal face-recognition standard. 

### **8.5 Processing Resolution** 

N-ONE has a processing-width cap of: 

1280 pixels 

This provides a practical limit on the width of frames entering the processing pipeline. 

The purpose of a processing-width cap is to prevent unnecessarily large frames from increasing computational requirements when a lower resolution is sufficient for the application's processing workflow. 

The actual recognition quality can still depend on the original camera resolution and the resulting face size within the frame. 

### **8.6 Duplicate-Suppression Configuration** 

N-ONE uses different write-throttling rules for different types of records. 

#### **Victim sightings** 

For Victim sightings, duplicate suppression is applied for the same profile and camera location under: 

60 seconds 

This prevents a continuously visible Victim from generating excessive duplicate entries within a short period. 

The concept can be represented as: 

Victim detected ↓ Check profile + location ↓ Recent record < 60 sec? /          \ Yes           No ↓             ↓ Suppress       Write event duplicate 

This does not mean that the Victim cannot be detected again during the interval. It means that duplicate audit writes are suppressed according to the implemented rule. 

#### **Unknown-person sightings** 

Unknown-person records use a different write interval: 

2 seconds per ID/location 

This allows repeated observations of an unknown individual to be recorded while preventing an excessive number of identical records from being generated for the same unknown ID and location. 

### **8.7 Authentication Security Configuration** 

The authentication system includes a login-attempt protection mechanism. 

The current configuration specifies: 

Maximum login attempts = 5 Lockout duration       = 60 seconds 

The simplified process is: 

Login Attempt ↓ Credential Check ↓ Failed? ↓       ↓ No      Yes ↓       ↓ Login   Increase failure count ↓ 5 failures? /     \ No       Yes ↓        ↓ Continue     Lockout 60 sec 

This provides a basic protection mechanism against repeated incorrect login attempts. 

It should not, however, be described as a complete enterprise authentication or identity-management system. The project uses application-level credentials and role controls rather than a full external identity provider. 

## **8.8 Complete Configuration Table** 

**Parameter Current Source Value / Status** 

Recognition model default Facenet 

|Detector default|opencv|
|---|---|
|Metric default|cosine|
|Threshold default|0.40|
|Processing width cap|1280pixels|
|Victim duplicate suppression|Same profile/location under 60 seconds|
|Unknown sighting write interval|2 seconds per ID/location|
|Maximum login attempts|5|
|Login lockout|60 seconds|
|Base Python target|Python 3.10+|
|Audited neural benchmark Python|3.12.10|
|Audited benchmark OS|Windows 11|
|Benchmark execution|CPU|
|Benchmark RAM measurement|Not available|
|Benchmark GPU measurement|Not measured|
|Application-wide FPS|Not measured|
|Guaranteed camera count|Not established|



## **8.9 Configuration Separation Between Production and Evaluation** 

An important part of N-ONE's configuration design is the separation between the **application's current production/default configuration** and the **experimental evaluation configuration** . 

The current application source configuration is: 

Facenet 

+ 

OpenCV detector + 

Cosine distance 

+ 

0.40 threshold 

The evaluation workspace can independently test different combinations such as: 

FaceNet 

FaceNet512 

ArcFace 

under controlled benchmark conditions. 

Therefore, an experimental result does not automatically change the live application's configuration. 

This separation is useful because it prevents an experimental model from silently becoming the application's operational model without verification. 

## **8.10 Configuration Security Considerations** 

Sensitive configuration values should be kept outside the academic report and source-controlled public files. 

Examples include: 

- Administrator password 

- Operator password 

- Streamlit secrets 

- API credentials 

- RTSP authentication information 

- Private camera URLs 

- Other environment-specific secrets 

The report should describe the **configuration mechanism** rather than exposing the actual secret values. 

For example, the report can state: 

ADMIN_USERNAME=<configured securely> ADMIN_PASSWORD=<stored outside source code> 

instead of documenting the real credential. 

## **8.11 System Configuration Summary** 

The N-ONE configuration consists of a Python-based software environment, an OpenCV fallback processing path, an optional DeepFace/TensorFlow neural runtime, multiple camera-ingestion mechanisms, and configurable recognition and logging parameters. 

The current recognition defaults are **FaceNet, OpenCV detection, cosine distance, and a 0.40 threshold** , while processing is capped at **1280 pixels width** . Victim duplicate records are suppressed for the same profile/location within **60 seconds** , while unknown-person sighting writes use a **2-second ID/location interval** . 

The authentication layer permits **five login attempts before a 60-second lockout** . 

Most importantly, the project does not currently provide enough measured evidence to define universal hardware requirements, guaranteed FPS, GPU requirements, RAM requirements, or maximum camera capacity. These values should be added from the actual final demonstration machine rather than estimated. 

## **CHAPTER 9 – BLOCK DIAGRAM AND SYSTEM ARCHITECTURE** 

The N-ONE system architecture describes how users, camera sources, processing modules, recognition components, and local storage interact with one another. The architecture is designed around a single Streamlit application in which the major functional modules are organized as logical processing boundaries. 

N-ONE follows a **monolithic application architecture** . This means that the dashboard, authentication logic, recognition workflow, threat-detection logic, unknown-person handling, and logging mechanisms operate within the same application rather than being deployed as independent microservices. 

The architecture can be divided into three major logical layers: 

1. **Presentation and access layer** 

2. **Processing and intelligence layer** 

3. **Local storage and audit layer** 

The application also contains an important **conditional AI boundary** . When the complete TensorFlow/DeepFace environment is available, the neural face-recognition path can be used. When it is unavailable, N-ONE can fall back to an OpenCV-based processing path with a defined safety boundary. 

## **9.1 Overall Architecture** 

The overall architecture begins with an authenticated Administrator or Operator and ends with processed results, inventory information, histories, and logs. 

The high-level workflow represented in the architecture is: 

Administrator / Operator ↓ 

Streamlit Security Gate ↓ Role and Session State ↓ Processing Mode Selection ↓ Video Source ↓ ┌────────┴───────────┐ ↓                    ↓ Browser / WebRTC    OpenCV-based Camera             Input Sources ↓                    ↓ └────────┬───────────┘ ↓ Mode ↓ ┌────────┼───────────────────┐ ↓        ↓                   ↓ Victim   Staff /          Threat Detection Search   Attendance ↓        ↓                   ↓ Face Recognition /      Possible Alert Matching                     ↓ ↓                       Audit Log Known / Unknown ↓ Unknown Cache ↓ CSV / Local Storage ↓ Inventory, Results, History and Logs 

This architecture illustrates that N-ONE does not send every frame through exactly the same processing operation. The selected operational mode determines which processing path is executed. 

### **9.1.1 Presentation Layer** 

The presentation layer is primarily implemented through the Streamlit dashboard. 

It provides the user interface for: 

- Login 

- Role selection through authenticated credentials 

- Profile registration 

- Camera selection 

- Victim Search 

- Staff/attendance operation 

- Threat Detection 

- Inventory viewing 

- Log inspection 

- Evaluation-related interfaces 

The dashboard also presents processed information to the operator, such as recognition results, possible threat alerts, unknown IDs, and Victim sighting information. 

The presentation layer therefore acts as the main interaction point between the human operator and the underlying processing modules. 

### **9.1.2 Authentication and Security Gate** 

The first architectural component is the authentication/security gate. 

Administrator / Operator ↓ Authentication ↓ Credential Validation ↓ Role Identification ↓ 

Session State 

The authenticated role controls access to different parts of the application. 

An Administrator can perform configuration and profile-management operations, while an Operator is primarily intended for monitoring, search, and review. 

This architecture prevents the operational dashboard from being treated as an unrestricted interface. 

### **9.1.3 Role and Session State** 

After successful authentication, N-ONE maintains the user's authentication and operational state through Streamlit session state. 

This state is used by the application to determine information such as: 

- Whether the user is authenticated 

- Current role 

- Selected operating mode 

- Selected Victim 

● Camera location 

- Latest recognition result 

The session state therefore connects the user interface with the processing workflow. 

## **9.2 Input and Video Source Architecture** 

After authentication and mode selection, N-ONE requires a visual input source. 

The architecture supports multiple types of sources. 

#### **Browser/WebRTC source** 

The browser camera path allows a user's camera to provide frames through WebRTC. 

Camera ↓ 

Browser ↓ WebRTC ↓ 

N-ONE 

This approach is useful when the application is being accessed remotely because the server does not need direct access to the client's physical camera. 

#### **Local OpenCV source** 

For a locally running deployment, OpenCV can access compatible webcams through the operating system. 

Local Webcam ↓ 

OpenCV ↓ 

N-ONE 

#### **Recorded video** 

A recorded video can also be supplied for processing. 

This is particularly useful during controlled evaluation because the same video can be processed repeatedly. 

#### **IP camera** 

An IP camera stream can be passed to OpenCV using a compatible stream URL. 

IP Camera 

↓ 

Network Stream ↓ 

OpenCV 

↓ 

##### N-ONE 

The exact performance of an IP-camera source depends on network conditions, stream configuration, resolution, and processing resources. 

## **9.3 Processing Mode Selection** 

After a video source is available, the application selects the appropriate processing mode. 

The major operational modes are: 

- **Victim Search** 

- **Staff/Attendance** 

- **Threat Detection** 

These modes do not use exactly the same processing logic. 

The architecture can therefore be represented as: 

Video Source ↓ Mode Selection ↓ ┌───────────────┼────────────────┐ ↓               ↓                ↓ Victim Search   Staff/Attendance   Threat Detection ↓               ↓                ↓ Face Matching    Face Matching     CV Heuristics ↓               ↓                ↓ Victim Result    Known/Unknown     Possible Alert 

This separation is important because the face-recognition system and the threat-detection system have different technical purposes. 

## **9.4 Face Recognition Processing Architecture** 

The face-recognition path is responsible for detecting faces, generating representations, comparing those representations with stored profiles, and producing a recognition decision. 

The general pipeline is: 

Frame ↓ Face Detection ↓ Face Region ↓ Face Representation ↓ Embedding / Feature Vector ↓ 

Known Cache ↓ Distance Comparison ↓ Threshold Decision ↓ 

Known / Unknown 

The architecture contains a DeepFace-compatible adapter so that the application can work with the configured neural runtime when its dependencies are available. 

The representation model may be configured according to the active environment. 

Models considered in the neural evaluation include: 

- FaceNet 

- FaceNet512 

- ArcFace 

The detector and representation model are separate components. For example, RetinaFace is a detector, whereas FaceNet and ArcFace are representation models. 

## **9.5 Conditional AI Boundary** 

One of the most important architectural elements in N-ONE is the conditional boundary between the neural runtime and the OpenCV fallback. 

The supplied architecture diagram represents this decision as: 

Frame ↓ DeepFace-compatible adapter ↓ TensorFlow / DeepFace 

available? 

/       \ Yes        No ↓          ↓ Selected      OpenCV Haar + neural model  HOG/CLAHE fallback and detector       ↓ ↓         Face detection / Embedding       fallback features comparison          ↓ ↓         Fallback safety Threshold            boundary decision               ↓ Detection-only 

This boundary prevents the application from assuming that the neural runtime is always available. 

### **9.5.1 Neural Processing Path** 

When TensorFlow/DeepFace is available, the application can use the selected neural model and detector. 

The conceptual workflow is: 

Frame ↓ DeepFace-compatible adapter ↓ Selected detector ↓ Face region ↓ Selected representation model ↓ Embedding ↓ Embedding comparison ↓ Cosine distance ↓ Threshold decision ↓ Recognition result 

The neural model generates a numerical representation of the detected face. That representation is compared with the stored representation associated with the candidate profile. 

A smaller cosine distance represents greater similarity. 

### **9.5.2 OpenCV Fallback Path** 

If the complete TensorFlow/DeepFace runtime is unavailable, the architecture follows the fallback branch. 

The fallback path uses: 

- OpenCV Haar detection 

- Grayscale processing 

- CLAHE enhancement 

- HOG feature extraction 

- Feature-vector normalization 

- Detection-box handling 

The conceptual pipeline is: 

Frame ↓ 

OpenCV Haar Detection ↓ 

Face Region ↓ Grayscale Processing ↓ 

CLAHE ↓ 

HOG Features ↓ 

Normalized Feature Vector 

This fallback should not be described as a neural face-recognition network. 

It is a lightweight computer-vision representation based on engineered features. 

## **9.6 Fallback Safety Boundary** 

The architecture explicitly contains a **fallback safety boundary** . 

This is an important design decision because the fallback processing path should not silently be represented as equivalent to the full neural identity-recognition system. 

The architecture indicates that the fallback can provide face detection and fallback features, but for high-impact Victim identification, the system maintains a conservative boundary. 

In particular, when the OpenCV fallback is being used, visible identity matching is disabled for the Victim Search path. The interface can therefore indicate that a face was detected without incorrectly labeling it as a specific Victim. 

This can be summarized as: 

Neural runtime available ↓ 

Identity matching possible ↓ 

Threshold decision ↓ Victim result 

Neural runtime unavailable ↓ OpenCV fallback ↓ Face detection / fallback features ↓ Safety boundary ↓ 

No unsupported Victim identity label 

This architecture is particularly important because a false Victim identification can have a much greater operational impact than simply reporting that a face was detected. 

## **9.7 Victim Search Architecture** 

Victim Search introduces an additional restriction into the recognition pipeline. 

The operator first selects a Victim profile and provides the camera location. 

The architecture then restricts the recognition search to the selected target. 

Operator ↓ 

Select Victim ↓ Enter Camera Location ↓ Video Frame 

↓ 

Face Detection ↓ 

Victim-specific Candidate 

↓ 

Embedding Comparison 

↓ 

Threshold Decision 

↓ 

Victim Found / No Match 

If a genuine target match is produced, the application can generate a Victim Found event. 

The result can include: 

- Victim profile 

- Profile ID 

- Camera location 

- Distance 

- Timestamp 

- Active model 

- Backend 

- Metric 

- Sighting history 

This target-restricted design is different from normal attendance recognition, where multiple registered profiles may be considered as candidates. 

## **9.8 Staff and Attendance Architecture** 

The Staff/Attendance path uses the general known-profile recognition workflow. 

Unlike Victim Search, it is not restricted to a single selected Victim. 

The conceptual process is: 

Frame ↓ Face Detection ↓ Face Representation ↓ Known Profile Cache ↓ Compare with Candidates ↓ 

Match? 

/   \ Yes   No ↓     ↓ Staff  Unknown Result Processing 

The system can therefore distinguish between registered people and unmatched observations. 

The Staff/Attendance workflow should be kept separate from the Victim Search workflow because their operational objectives are different. 

## **9.9 Unknown Re-ID Architecture** 

When a detected face does not match the appropriate known-profile cache, N-ONE can enter the unknown-person processing path. 

The architecture is: 

Known Profile Match ↓ No Match ↓ Unknown Cache ↓ Previously observed? /       \ Yes        No ↓          ↓ Update       Create record       unknown ID ↓          ↓ Update       Save crop history      + metadata \      / ↓    ↓ Sighting Log 

New unknown individuals receive locally generated identifiers such as: 

unknown_001 unknown_002 unknown_003 

These identifiers do not represent the person's real-world identity. 

They represent a locally maintained identity for repeated observations within the N-ONE system. 

## **9.10 Threat Detection Architecture** 

Threat Detection is an independent processing branch. 

It does not use FaceNet, FaceNet512, ArcFace, or the face-recognition cosine threshold. 

Instead, the architecture uses image-processing heuristics. 

Video Frame ↓ Canny Edge Detection ↓ Morphological Processing ↓ Contour Analysis ↓ Warm HSV Mask ↓ Heuristic Evaluation ↓ Possible Threat / Fire Alert ↓ Audit Logging 

The result is intentionally represented as a **possible threat/fire indication** . 

It should not be described as a verified weapon classifier or as a deep-learning weapon-detection model. 

Human review remains necessary before interpreting or acting upon such an alert. 

## **9.11 Data Storage Architecture** 

N-ONE uses local files and CSV-based storage rather than a separate database server. 

The storage layer can contain information related to: 

#### **Registered profiles** 

Staff_<id>.jpg Victim_<id>.jpg 

**Unknown profiles** unknown_001.jpg unknown_002.jpg 

#### **Unknown-person database** 

unknown_person_db.csv 

#### **Unknown sighting history** 

unknown_sighting_log.csv 

#### **Victim sighting records** 

victim_sighting_log.csv 

Additional audit information can also be stored according to the project's logging implementation. The architecture therefore uses the local filesystem and CSV records as the persistence mechanism. 

## **9.12 Dashboard and Result Layer** 

After processing, results return to the dashboard. 

The dashboard can display: 

- Recognition results 

- Victim Found information 

- Unknown IDs 

- Camera location 

- Timestamps 

- Registered-profile information 

- Log information 

- Evaluation metrics 

The overall output path is: 

Processing ↓ 

Result Generation ↓ Dashboard ↓ Local Logs ↓ Review / Analysis 

This provides a closed operational loop from camera input to human review. 

## **9.13 Local Storage Instead of Database Server** 

An important architectural characteristic is that N-ONE is currently a **monolithic local-storage application** . 

The project does not use a separate database server as its primary persistence layer. 

Instead, it relies on: 

- Local image files 

- CSV files 

- Application state 

- Structured log files 

This approach simplifies deployment and makes the project easier to demonstrate in a university environment. 

However, it also introduces limitations related to: 

- Concurrent access 

- Large-scale storage 

- Multi-user synchronization 

- Database transactions 

- Centralized backup 

- Large-scale multi-camera deployments 

These limitations should be considered if the system is extended beyond its current project scope. 

## **9.14 Complete Module Architecture** 

The major modules described in Chapter 6 can be placed into the architecture as follows: 

N-ONE APPLICATION │ Authentication / RBAC │ Streamlit Dashboard │ Processing Mode Selection │ ┌─────────────┼─────────────┐ ↓             ↓             ↓ Victim Search   Attendance   Threat Detection │             │             │ └──────┬──────┘             │ ↓                    ↓ Face Recognition        CV Heuristic Path │                    │ 



<!-- Start of picture text -->
       ┌─────────┴─────────┐          │<br>       ↓                   ↓          ↓<br> Neural Runtime       OpenCV Fallback Alert<br>       │                   │          │<br>↓ ↓ │<br> Embedding            HOG Features    │<br> Comparison               │           │<br>↓ │ │<br> Threshold Decision       │           │<br>       └──────────┬────────┘           │<br>↓ │<br>          Known / Unknown              │<br>↓ │<br>          Unknown Re-ID                │<br>                  │                    │<br>                  └──────────┬─────────┘<br>                             ↓<br>                     Local Storage<br>                             ↓<br>                     Dashboard Review<br><!-- End of picture text -->

## **9.15 Three-Layer Architectural View** 

For documentation purposes, the architecture can also be divided into three logical layers. 

#### **Layer 1 – Presentation Layer** 

Contains: 

- Streamlit interface 

- Login interface 

- Dashboard 

- Controls 

- Result cards 

- Inventory and log views 

#### **Layer 2 – Processing Layer** 

Contains: 

- Camera ingestion 

- Face detection 

- Face representation 

- Face matching 

- Victim Search 

- Staff recognition 

- Unknown Re-ID 

- Threat Detection 

- Evaluation processing 

#### **Layer 3 – Storage Layer** 

Contains: 

- Registered face images 

- ● Unknown face images ● CSV metadata ● Victim sighting records 

- Unknown sighting records 

- Audit information 

The architecture can therefore be summarized as: 

┌──────────────────────────────────────┐ │         PRESENTATION LAYER           │ │       Streamlit Dashboard            │ │  Login | Search | Monitoring | Logs  │ └──────────────────┬───────────────────┘ ↓ ┌──────────────────────────────────────┐ │          PROCESSING LAYER             │ │ Face Recognition | Victim Search      │ │ Staff | Unknown Re-ID | Threat        │ │ Camera / Video Processing             │ └──────────────────┬───────────────────┘ ↓ ┌──────────────────────────────────────┐ │            STORAGE LAYER              │ │ Profiles | Unknowns | CSV Logs       │ │ Victim Sightings | Audit Records     │ └──────────────────────────────────────┘ 

## **9.16 Figure Interpretation** 

The architecture figures supplied for this chapter should be interpreted as complementary views of the same system. 

#### **Figure 9.1 – Overall System Architecture** 

The overall architecture figure shows the movement from: 

**Administrator/Operator → Security Gate → Role/Session State → Processing Mode → Video Source → Processing → Results → Inventory/Logs/History** 

This figure provides the broad system-level view. 

#### **Figure 9.2 – Conditional AI Boundary** 

The conditional AI diagram focuses specifically on the runtime decision between the neural DeepFace/TensorFlow path and the OpenCV fallback path. 

It demonstrates that the availability of the neural runtime determines which processing route is used. 

#### **Figure 9.3 – Module Architecture** 

The module architecture should represent the major modules discussed in Chapter 6: 

- Authentication/RBAC 

- Registration 

- Camera Ingestion 

- Face Recognition 

- Victim Search 

- Staff/Attendance 

- Unknown Re-ID 

- Threat Detection 

- Dashboard/Logs 

- Evaluation 

#### **Figure 9.4 – Storage Architecture** 

The storage figure should show how registered profiles, unknown profiles, Victim sightings, unknown sightings, and audit information are persisted locally. 

#### **Figure 9.5 – Recognition Pipeline** 

The recognition pipeline figure should show: 

Frame ↓ Detection ↓ Representation ↓ Known Cache ↓ Distance Comparison ↓ Threshold ↓ Known / Unknown 

with the conditional neural/fallback boundary represented where appropriate. 

## **9.17 Architectural Characteristics** 

The N-ONE architecture has several important characteristics. 

#### **Monolithic design** 

All major components currently operate within the same application rather than separate services. 

#### **Modular internal organization** 

Although the application is monolithic, its functional responsibilities are separated into logical modules. 

#### **Conditional AI runtime** 

The neural recognition path depends on the availability of the required runtime and dependencies. 

#### **Explicit fallback** 

The OpenCV fallback provides a controlled alternative rather than silently pretending that the neural models are available. 

#### **Target-restricted Victim Search** 

Victim Search narrows the recognition candidate set to the selected Victim. 

#### **Separate threat-processing path** 

Threat detection is independent of face-recognition models. 

#### **Local persistence** 

Images and operational records are maintained through local files and CSV-based storage. 

#### **Human review** 

Recognition results and threat alerts are intended to support operator review rather than completely replace human decision-making. 

## **9.18 Architectural Limitations** 

The current architecture also has limitations. 

Because the application is monolithic, scaling individual services independently is not currently part of the design. 

The local CSV/file-based persistence model is suitable for the current project workflow but is not equivalent to a centralized production database architecture. 

The conditional neural runtime means that recognition capabilities depend on the environment in which the application is executed. 

The OpenCV fallback also has different characteristics from neural face recognition and therefore should not be treated as a replacement with equivalent identity-recognition capability. 

Finally, the architecture does not by itself establish a specific FPS, maximum number of cameras, universal recognition accuracy, or production-scale deployment capability. Those properties require separate measurements under defined test conditions. 

## **9.19 Overall Architecture Summary** 

The N-ONE architecture integrates authentication, role-based access, camera ingestion, operationalmode selection, face recognition, Victim Search, Staff recognition, Unknown Re-ID, threat analysis, local storage, and result review within a single Streamlit application. 

Its most important architectural feature is the **conditional AI boundary** . When the TensorFlow/DeepFace environment is available, the system can use a selected neural representation model and detector. When that runtime is unavailable, the application follows an OpenCV-based fallback path with a defined safety boundary. 

The architecture also deliberately separates **identity recognition from threat detection** . Face recognition uses face representations and distance-based matching, whereas threat monitoring uses OpenCV-based image-processing heuristics. 

Consequently, the block diagram represents N-ONE not as a single AI model, but as an integrated collection of processing modules connected through a common dashboard, local storage system, and human-operated workflow. 

## **CHAPTER 10 – DATA FLOW DIAGRAMS** 

The Data Flow Diagram (DFD) of N-ONE describes how information moves between the users, application processes, camera/input sources, recognition modules, threat-detection logic, and local storage. The DFD focuses on **data movement and transformation** , rather than the internal programming implementation. 

Since N-ONE is implemented as a monolithic Streamlit application with local image and CSVbased persistence, the DFD represents the logical movement of data through the application rather than communication between independent servers or database services. 

The main data flows include: 

- User authentication data 

- Role and session information 

- Profile-registration data 

- Camera/video frames 

- Face-detection data 

- Face representations 

- Recognition results 

- Unknown-person records 

- Victim Search results 

- Threat-analysis results 

- Camera-location information 

- Sighting records 

- Audit information 

- Evaluation results 

## **10.1 Context DFD** 

The **Context DFD** provides the highest-level view of N-ONE. At this level, the entire N-ONE application is treated as a single process. 

The external entities interacting with the system are primarily: 

- **Administrator** 

- **Operator** 

- **Camera / Video Source** 

The system returns processed results, alerts, records, and status information to the appropriate user. 

#### **Context-level representation** 



<!-- Start of picture text -->
                        ┌─────────────────────┐<br>                         │    Administrator     │<br>                         └──────────┬──────────┘<br>                                    │<br>                    Login / Profiles / Configuration<br>                                    │<br>                                    ↓<br>                         ┌─────────────────────┐<br>                         │                     │<br>                         │       N-ONE         │<br>                         │ AI-Assisted         │<br>                         │ Surveillance System │<br>                         │                     │<br>                         └─────────────────────┘<br>                                    ↑<br>                                    │<br>                       Results / Status / Logs<br>                                    │<br>                         ┌──────────┴──────────┐<br>                         │                     │<br>                         │                     │<br>                ┌────────┴────────┐   ┌───────┴────────┐<br><!-- End of picture text -->

│    Operator     │   │ Camera / Video │ └─────────────────┘   │     Source     │ └────────────────┘ 

#### **Administrator data flow** 

The Administrator provides information such as: 

- Login credentials 

- Staff profile information 

- Victim profile information 

- Registration images 

- Model configuration 

- Administrative commands 

##### N-ONE returns: 

- Authentication status 

- Registration status 

- Profile information 

- Configuration status 

- Dashboard information 

#### **Operator data flow** 

The Operator provides: 

- Login credentials 

- Selected Victim 

- Camera location 

- Monitoring commands 

- Search requests 

- Review requests 

##### N-ONE returns: 

- Recognition results 

- Victim Found information 

- Unknown-person information 

- Possible threat/fire alerts 

- Logs and sighting history 

- Dashboard status 

#### **Camera/video data flow** 

Camera and video sources provide: 

- Image frames 

- Video frames 

- Camera-source information 

The system processes these inputs and produces recognition, unknown-person, or threat-analysis results. 

## **10.2 Level-0 DFD** 

The Level-0 DFD decomposes the complete N-ONE application into its major logical processes. 

The main processes are: 

1. **Authentication and RBAC** 

2. **Profile Registration** 

3. **Camera and Frame Processing** 

4. **Face Recognition / Matching** 

5. **Unknown Re-ID** 

6. **Victim Search** 

7. **Threat Detection** 

8. **Logging and Dashboard Review** 

The major data stores are local image directories and CSV files. 

#### **Level-0 logical flow** 



<!-- Start of picture text -->
Administrator<br>     │<br>     │ Credentials<br>     ↓<br>┌─────────────────────┐<br>│ 1. Authentication   │<br>│      and RBAC       │<br>└──────────┬──────────┘<br>           │<br>           │ Role / Session<br>           ↓<br>┌─────────────────────┐<br>│ 2. Profile          │<br>│    Registration     │<br>└──────────┬──────────┘<br>           │<br>           │ Profile Images<br>           ↓<br>   Registered Profiles<br>       Data Store<br><!-- End of picture text -->



<!-- Start of picture text -->
Camera / Video<br>      │<br>      │ Frames<br>      ↓<br>┌─────────────────────┐<br>│ 3. Camera / Frame   │<br>│    Processing       │<br>└──────────┬──────────┘<br><!-- End of picture text -->

│ ↓ 

Mode Selection 



<!-- Start of picture text -->
           │<br>     ┌─────┼───────────────┐<br>     ↓     ↓               ↓<br>Victim   Staff          Threat<br>Search   /Attendance    Detection<br>     │     │               │<br>     └─────┼───────────────┘<br>           ↓<br>┌─────────────────────┐<br>│ 4. Face Recognition │<br>│    / Matching       │<br>└──────────┬──────────┘<br>           │<br>     Known / Unknown<br>           │<br>      ┌────┴─────┐<br>      ↓          ↓<br>   Known      Unknown<br>      │          │<br>      ↓          ↓<br> Results     ┌──────────────┐<br>             │ 5. Unknown  │<br>             │    Re-ID    │<br>             └──────┬───────┘<br>                    ↓<br>              Unknown Records<br><!-- End of picture text -->



<!-- Start of picture text -->
Results / Alerts<br>       ↓<br>┌─────────────────────┐<br>│ 8. Logging and      │<br>│    Dashboard Review │<br>└──────────┬──────────┘<br>           ↓<br>      User / Operator<br><!-- End of picture text -->

This Level-0 view provides a logical decomposition of the system without representing individual Python functions. 

## **10.3 Authentication and RBAC Data Flow** 

Authentication is the first major data-processing stage. 

Administrator / Operator │ │ Username + Password ↓ Authentication Process │ ↓ Credential Check │ Valid? /    \ Yes     No │       │ ↓       ↓ Role Set   Error / │     Login Reject ↓ Session State │ ↓ Role-specific Dashboard 

The authentication process does not send the user's password into the recognition pipeline. 

Instead, successful authentication establishes the role and session state that control subsequent access. 

## **10.4 Profile Registration Data Flow** 

Profile registration is mainly an Administrator-driven process. 

Administrator │ │ Profile Information │ + Image / Camera Capture ↓ Profile Registration │ ↓ Image Decode │ ↓ 

Face Detection │ ↓ 

Exactly One Face? 

/       \ No         Yes │           │ Reject       Face Crop │ ↓ 25% Padding │ ↓ Profile ID Creation │ ↓ 

Staff / Victim Image Store 

The registration data therefore changes from a raw image into a controlled face-profile image. 

The resulting profile is stored locally and later becomes part of the known-profile cache used by recognition. 

## **10.5 Camera and Frame Processing DFD** 

The camera-processing process receives visual data from one of the supported sources. 

Possible sources include: 

- Browser/WebRTC camera 

- Local webcam 

- Recorded video 

- IP camera stream 

The flow is: 

Camera / Video Source ↓ Frame Input ↓ Frame Processing ↓ Resolution / Image Preparation ↓ Selected Mode 

At this point the system determines whether the frame should enter: 

- Face recognition 

- Victim Search 

- Staff/attendance 

- Threat Detection 

## **10.6 Face Recognition Data Flow** 

The face-recognition DFD describes the transformation of a camera frame into a recognition result. 

Camera Frame ↓ Face Detection ↓ Detected Face Region ↓ Face Representation ↓ Embedding / Feature Vector ↓ Known Profile Cache ↓ Distance Comparison ↓ Threshold Decision ↓ 

Known / No Match 

When the neural runtime is available, the representation can be generated using the selected neural model. 

When the fallback runtime is active, the OpenCV-based representation path is used according to the application's safety boundary. 

## **10.7 Victim Search DFD** 

Victim Search has a more restricted data flow than normal recognition because the operator selects a specific Victim before starting the search. 

The major input data are: 

- Selected Victim profile 

- Camera location 

- Video/image frames 

The flow is: 

Operator │ ├── Select Victim │ └── Enter Camera Location │ ↓ Victim Search Process │ ↓ Camera Frame │ ↓ Face Detection │ ↓ Selected Victim Cache │ ↓ Embedding Comparison │ ↓ Distance Value │ ↓ Threshold Decision /       \ Match     No Match │          │ ↓          ↓ Victim Found   Continue │ ↓ Sighting Record │ ↓ Dashboard Card 

When a valid target match occurs, the resulting Victim Found event can contain: 

- Victim profile ID 

- Victim image 

- Camera location 

- Recognition distance 

- Timestamp 

- Active model 

- Backend 

- Metric 

- Sighting history 

This information is then made available to the operator and relevant local logs. 

## **10.8 Unknown Re-ID Data Flow** 

Unknown Re-ID is activated when a detected face does not produce a suitable known-profile match. 

The data flow is: 

Detected Face ↓ Known Profile Comparison ↓ No Match ↓ Unknown Cache Comparison ↓ Existing Unknown? /          \ Yes           No │             │ ↓             ↓ Update         Generate Unknown ID     Unknown ID │             │ ↓             ↓ Update         Save Face Crop Metadata       + Metadata │             │ └──────┬──────┘ ↓ Sighting Record ↓ unknown_sighting_log.csv 

A new unknown receives an identifier such as: 

unknown_001 

A later observation can be associated with the same local unknown identifier if the system determines that the observation corresponds to an existing unknown record. 

This provides repeated-observation context without claiming the person's real-world identity. 

## **10.9 Threat Detection DFD** 

Threat Detection follows an independent data flow. 

Camera Frame ↓ Canny Edge Detection ↓ Morphological Processing ↓ Contour Geometry ↓ Warm HSV Mask ↓ Heuristic Analysis ↓ Possible Threat / Fire ↓ Alert Throttling ↓ Audit Record ↓ 

Dashboard 

The important point is that this data flow does not contain the face-recognition embedding or cosine-distance process. 

Therefore, the Threat Detection DFD should not represent FaceNet, FaceNet512, or ArcFace as part of the threat-analysis pipeline. 

## **10.10 Logging and Data Flow** 

After processing, important events are written to the appropriate local storage mechanism. 

The major logical records include: 

#### **Registered profiles** 

Staff_<id>.jpg Victim_<id>.jpg 

#### **Unknown-person information** 

unknown_person_db.csv 

#### **Unknown sightings** 

unknown_sighting_log.csv 

#### **Victim sightings** 

victim_sighting_log.csv 

The flow can be represented as: 

Processing Result ↓ Determine Event Type ↓ ┌─────┼──────────┬─────────────┐ ↓     ↓          ↓             ↓ Victim Unknown  Threat       General Event   Event    Alert        Audit ↓       ↓        ↓             ↓ CSV     CSV      CSV/Log      Audit \    |       |          / \   |       |         / Local Storage 

The actual project storage is based on local files and CSV records rather than a SQL database server. 

## **10.11 Data Store Description** 

The N-ONE DFD uses logical data stores to represent the project's actual filesystem and CSV persistence. 

#### **D1 – Registered Profile Store** 

Contains the face-only images associated with registered Staff and Victim profiles. 

Example: 

Staff_<id>.jpg Victim_<id>.jpg 

#### **D2 – Unknown Profile Store** 

Contains locally stored face crops associated with unknown IDs. 

Example: 

unknown_001.jpg unknown_002.jpg 

#### **D3 – Unknown Person Database** 

unknown_person_db.csv 

Contains metadata associated with locally re-identified unknown persons. 

#### **D4 – Unknown Sighting Log** 

unknown_sighting_log.csv 

Contains repeated observations associated with unknown IDs. 

#### **D5 – Victim Sighting Log** 

victim_sighting_log.csv 

Contains Victim Found/sighting information, including location and timestamp information. 

#### **D6 – Audit/Operational Records** 

The application also maintains audit-oriented operational information according to the implemented logging system. 

These records support review and evaluation of application behavior. 

## **10.12 Data Flow Between Modules** 

The complete logical data flow can be summarized as: 

USER │ ↓ Authentication │ ↓ 

Role / Session │ ↓ Dashboard │ ↓ Mode + Camera │ ↓ Frame Processing │ ┌─────────┼─────────┐ ↓         ↓         ↓ Victim     Staff     Threat Search   Attendance  Detection │         │         │ └────┬────┘         │ ↓              ↓ Face Recognition   CV Heuristics │              │ ┌─────┴─────┐        │ ↓           ↓        ↓ Known       Unknown   Alert │           │        │ │ ↓ │ │        Unknown    │ │          Re-ID    │ │           │        │ └─────┬─────┴────────┘ ↓ Event / Result ↓ Local Data Store ↓ Dashboard Review 

## **10.13 Level-1 Victim Search DFD** 

For a more detailed representation of Victim Search, the process can be divided into smaller subprocesses. 

P1 – Select Victim ↓ 

P2 – Receive Camera Location 

P3 – Acquire Frame ↓ 

P4 – Detect Face ↓ 

P5 – Generate Representation ↓ 

P6 – Compare with Selected Victim ↓ 

P7 – Calculate Distance ↓ 

P8 – Apply Threshold ↓ ┌────┴─────┐ ↓          ↓ Match       No Match ↓          ↓ P9          Continue Victim Found ↓ P10 – Record Sighting ↓ 

- P11 – Display Result 

This Level-1 representation shows that Victim Search is not simply a single recognition function. It is a sequence of input collection, target selection, visual processing, comparison, decision, logging, and presentation steps. 

## **10.14 Data Flow and Human Review** 

An important characteristic of the N-ONE DFD is that processed information ultimately reaches a human operator. 

The system does not represent the final action as an automatic real-world decision. 

Instead: Camera Data ↓ Automated Processing ↓ Recognition / Alert ↓ 

Dashboard 

↓ Human Review 

- ↓ 

Operator Decision 

This is particularly important for: 

- Victim identification 

- Possible threat alerts 

- Unknown-person observations 

The automated system produces information and evidence for review, while the operator provides contextual interpretation and decides what action, if any, is appropriate. 

## **10.15 DFD and System Boundaries** 

The DFD also establishes what is **inside** and **outside** the current N-ONE implementation. 

#### **Inside the system** 

- Authentication 

- RBAC 

- Registration 

- Image processing 

- Face detection 

- Face representation 

- Recognition 

- Victim Search 

- Unknown Re-ID 

- Threat heuristics 

- Logging 

- Dashboard 

- Local persistence 

- Evaluation workspace 

#### **Outside the system** 

- Physical camera hardware 

- Browser camera hardware 

- External IP cameras 

- Operating-system camera drivers 

- Human operator decisions 

- External network infrastructure 

This distinction is important when discussing project limitations because N-ONE does not control every component involved in the complete surveillance environment. 

## **10.16 DFD Limitations** 

The current DFD represents the logical data flow of the implemented monolithic application. It should not be interpreted as evidence that the system uses independent distributed services. 

The application currently does not use a separate SQL database as its primary persistence mechanism. Therefore, the data stores shown in the DFD correspond to actual image directories and CSV-based storage rather than relational database tables. 

Similarly, the DFD does not establish performance characteristics such as: 

- Guaranteed FPS 

- Maximum camera count 

- Maximum concurrent users 

- Maximum database size 

- Guaranteed recognition accuracy 

Those characteristics require separate measurements. 

## **10.17 Summary** 

The N-ONE Data Flow Diagrams provide a logical representation of how information moves through the application. 

At the context level, the system receives information from administrators, operators, and camera/video sources and returns processed results and records. 

At Level 0, the application is decomposed into authentication, registration, frame processing, face recognition, Unknown Re-ID, Victim Search, Threat Detection, and logging/review processes. 

The Victim Search DFD further demonstrates the target-specific workflow in which an operator selects a Victim, provides a camera location, processes incoming frames, compares the detected face against the selected target, applies the configured threshold, and records a Victim Found event when a valid match occurs. 

The data stores are represented by the project's actual image directories and CSV files. Because N- ONE does not currently implement a SQL database, the logical entities and relationships documented in the following chapter should be understood as **documentation models derived from the actual file-based data structures** , rather than as a deployed relational database schema. 

## **CHAPTER 11 – LOGICAL ER / DATA MODEL** 

The N-ONE application uses local image files, CSV files, application session state, and event records to maintain operational information. Unlike a conventional database-driven application, the current implementation does **not** create a relational SQL database containing tables, primary keys, foreign keys, and database-enforced relationships. 

Therefore, the ER model presented in this chapter is a **logical data model** . It describes the entities and relationships represented by the application's actual data structures and processing workflow. It should not be interpreted as evidence that these entities are physically implemented as SQL tables. 

### **11.1 Purpose of the Logical Data Model** 

The logical data model provides a structured view of the information handled by N-ONE. 

The main objectives are to represent: 

- Authenticated user/session information 

- Registered Staff and Victim profiles 

- Unknown-person records 

- Repeated unknown sightings 

- Victim sightings 

- Audit events 

- Camera/location context 

The model helps explain how information generated during monitoring is associated with a person, observation, location, timestamp, or operational event. 

The simplified relationship can be represented as: 

User Session │ │ operates ↓ Camera Context │ │ provides context for ↓ Operational Event │ ├───────────────┐ ↓               ↓ Profile         Unknown Person │                  │ │                  │ ↓                  ↓ Victim            Unknown Sighting          Sighting 

Audit records provide a broader record of operational activity across these processes. 

## **11.2 Logical Entities** 

The major logical entities in the N-ONE data model are: 

1. User Session 

2. Profile 

3. Unknown Person 

4. Unknown Sighting 

5. Victim Sighting 

6. Audit Record 

7. Camera Context 

Each entity represents a logical information object rather than a physical SQL table. 

## **11.3 User Session Entity** 

The **User Session** represents the authenticated state of the person currently using N-ONE. Important logical attributes include: 

**Attribute Description** 

Role Administrator or Operator Authentication State Indicates whether the user is authenticated 

Selected Settings Runtime settings selected during the session 

The session is maintained through the application's Streamlit session state. 

#### **Role** 

The role determines which functionality is available to the authenticated user. 

The primary roles are: 

Administrator 

Operator 

The Administrator has access to management/configuration functions, while the Operator primarily performs monitoring and review operations. 

#### **Authentication State** 

The authentication state indicates whether the current session has successfully passed the application's credential check. 

#### **Selected Settings** 

The session can also contain runtime selections relevant to the current operation, such as the selected mode or Victim. 

## **11.4 Profile Entity** 

The **Profile** entity represents a registered Staff or Victim. 

A logical Profile can contain: 

##### **Attribute** 

##### **Description** 

Profile ID Unique application-level profile identifier 

Name Registered person's name 

Category Staff or Victim 

Image Path Location of the stored profile image 

Angle Capture/view angle associated with the image 

The category distinguishes between: 

Staff 

Victim 

This distinction is important because the operational behavior differs between normal Staff recognition and target-restricted Victim Search. 

#### **Profile images** 

The application stores face-only profile images using the project's naming convention, for example: 

Staff_<profile_id>.jpg Victim_<profile_id>.jpg 

A profile may have images corresponding to different capture angles. 

The logical structure can therefore be represented as: 

Profile │ ├── Profile ID ├── Name ├── Category └── Image 

└── Angle 

The model describes the logical relationship between a profile and its image information; it does not claim that these values are stored in a single database row. 

## **11.5 Unknown Person Entity** 

The **Unknown Person** entity represents an individual who has been observed by N-ONE but has not been matched to a registered Staff or Victim profile. 

The application assigns a local identifier such as: 

unknown_001 unknown_002 unknown_003 

The important logical attributes are: 

|**Attribute**|**Description**|
|---|---|
|Unknown ID|Local identifier assigned by N-ONE|
|Image Path|Stored face-crop location|
|First Timestamp|First recorded observation|
|Last Timestamp|Most recent recorded observation|
|Last Location|Latest associated camera location|
|Optional Assigned Name|Optional name field if available|



The term **Unknown Person** is important because the ID does not necessarily represent the person's real-world identity. 

For example: 

unknown_001 

means that N-ONE has associated repeated observations with the same local unknown record. It does not establish the person's legal name or actual identity. 

## **11.6 Unknown Sighting Entity** 

The **Unknown Sighting** represents an individual observation associated with an Unknown Person. 

Its logical attributes include: 

##### **Attribute Description** 

Sighting ID Identifier for the observation 

Unknown ID Associated local unknown identifier 

Timestamp Time of observation 

Location Camera/operator-entered location 

The relationship is: 

Unknown Person │ │ has ↓ 

Unknown Sighting │ ├── Sighting ID ├── Timestamp └── Location 

Conceptually, one Unknown Person can have multiple sightings: 

unknown_001 │ ├── Sighting 001 ├── Sighting 002 ├── Sighting 003 └── Sighting 004 

This structure supports the Unknown Re-ID workflow. 

The application can update the last-known information for the Unknown Person while maintaining individual sighting records. 

## **11.7 Victim Sighting Entity** 

The **Victim Sighting** represents a recorded observation associated with a registered Victim profile. 

Its logical attributes include: 

**Attribute Description** 

Profile ID Associated Victim profile 

Name Victim name Timestamp Time of observation Location Camera location 

A simplified relationship is: 

Victim Profile │ │ detected in ↓ Victim Sighting │ ├── Timestamp └── Location 

A single Victim profile can therefore have multiple recorded sightings. 

For example: 

Victim A │ ├── Location A / Time 1 ├── Location B / Time 2 └── Location C / Time 3 

This allows the application to provide a location-aware history of Victim observations. 

## **11.8 Audit Record Entity** 

The **Audit Record** represents an operational event recorded by the application. 

The logical attributes include: 

**Attribute** 

**Description** 

Timestamp Time at which the event occurred 

Mode Active operational mode 

Subject ID Associated profile or unknown ID where applicable 

Role User role associated with the operation 

Event Type Type of event generated 

Details Additional event information 

Possible operational contexts include: 

- Victim Search 

- Staff/Attendance 

- Unknown Re-ID 

- Threat Detection 

- Other application operations 

The logical structure is: 

Audit Record │ ├── Timestamp ├── Mode ├── Subject ID ├── Role ├── Event Type └── Details 

The audit record provides a broader event-oriented view than an individual Victim or Unknown sighting. 

## **11.9 Camera Context Entity** 

The **Camera Context** represents the location information entered by the operator for the active monitoring source. 

Its primary logical purpose is to associate an observation with a meaningful location. 

For example: 

Camera Context │ └── Location 

The location can then be associated with: 

- Victim sightings 

- Unknown sightings 

- Operational events 

This creates a basic relationship between an observation and the camera context under which it occurred. 

The camera context should not be interpreted as a complete physical camera inventory system unless such a database is separately implemented. 

## **11.10 Logical Relationship Diagram** 

The entities can be represented through the following logical ER-style structure: 



<!-- Start of picture text -->
┌──────────────────────┐<br>│     USER SESSION     │<br>├──────────────────────┤<br>│ Role                 │<br>│ Authentication State │<br>│ Selected Settings    │<br>└──────────┬───────────┘<br>           │<br>           │ operates<br>           ↓<br>┌──────────────────────┐<br>│   CAMERA CONTEXT     │<br>├──────────────────────┤<br>│ Location             │<br>└──────────┬───────────┘<br>           │<br>           │ provides context<br>           ↓<br>┌──────────────────────┐<br>│    AUDIT RECORD      │<br>├──────────────────────┤<br>│ Timestamp            │<br>│ Mode                 │<br>│ Subject ID           │<br>│ Role                 │<br>│ Event Type           │<br>│ Details              │<br>└──────────────────────┘<br><!-- End of picture text -->



<!-- Start of picture text -->
┌──────────────────────┐<br>│       PROFILE        │<br>├──────────────────────┤<br>│ Profile ID           │<br>│ Name                 │<br>│ Category             │<br>│ Image Path           │<br>│ Angle                │<br>└──────────┬───────────┘<br>           │<br>      ┌────┴───────────┐<br>      │                │<br>      │                │<br>      ↓                ↓<br>┌──────────────┐  ┌──────────────────┐<br>│   VICTIM     │  │ UNKNOWN PERSON   │<br>│   SIGHTING   │  │                  │<br>├──────────────┤  ├──────────────────┤<br>│ Profile ID   │  │ Unknown ID       │<br>│ Name         │  │ Image Path       │<br>│ Timestamp    │  │ First Timestamp  │<br>│ Location     │  │ Last Timestamp   │<br>└──────────────┘  │ Last Location    │<br>                  │ Optional Name    │<br>                  └────────┬─────────┘<br>                           │<br>                           │ has<br>                           ↓<br>                  ┌──────────────────┐<br>                  │ UNKNOWN SIGHTING │<br>                  ├──────────────────┤<br>                  │ Sighting ID      │<br>                  │ Unknown ID       │<br>                  │ Timestamp        │<br>                  │ Location         │<br>                  └──────────────────┘<br><!-- End of picture text -->

This diagram is a **logical representation** of the application's data relationships. 

## **11.11 Relationship Description** 

The major logical relationships can be described as follows. 

#### **User Session → Camera Context** 

An authenticated user operates the application and provides or selects the camera context used during monitoring. 

#### **Profile → Victim Sighting** 

A registered Victim profile can be associated with one or more Victim sightings. 

One Profile ↓ Multiple Victim Sightings 

#### **Unknown Person → Unknown Sighting** 

A locally identified unknown person can have multiple recorded sightings. 

One Unknown Person ↓ 

Many Unknown Sightings 

#### **Camera Context → Sighting** 

A camera/location context can be associated with multiple observations. 

For example: 

Camera Location A │ ├── Victim Sighting ├── Unknown Sighting └── Operational Event 

#### **User Session → Audit Record** 

Operations performed during an authenticated session can be associated with the user's role in audit-oriented records. 

## **11.12 Logical Model and Actual File Storage** 

The logical entities described above correspond to information maintained by the current implementation, but they are not physically stored as relational database tables. 

The actual persistence mechanism uses files and CSV records. 

A conceptual mapping is: 

##### **Logical Entity Current Physical Representation** 

|User Session|Streamlit session state|
|---|---|
|Profile|Image files + application metadata|
|Unknown Person|Unknown image files +unknown_person_db.csv|
|Unknown Sighting|unknown_sighting_log.csv|
|Victim Sighting|victim_sighting_log.csv|
|Audit Record|Application audit/log records|
|Camera Context|Runtime/event information associated with observations|



This distinction is essential for technical accuracy. 

For example, the following diagram: 

PROFILE │ └──────< VICTIM SIGHTING 

means that a logical profile can be associated with multiple Victim sightings. 

It does **not** mean that N-ONE contains a SQL table called PROFILE with a foreign-key relationship to a table called VICTIM_SIGHTING. 

## **11.13 File-Based Data Architecture** 

The physical storage architecture can be represented as: 

N-ONE │ Local Storage │ ┌───────────┼────────────┐ ↓           ↓            ↓ Registered     Unknown       Logs Profiles       Profiles        │ │           │            │ ↓ ↓ ┌─────┼──────────────┐ Staff_*.jpg   unknown_*.jpg  ↓     ↓           ↓ Victim_*.jpg             Victim  Unknown     Audit 

Logs    Logs        Records 

This structure is simpler than a conventional database schema but is sufficient for the current application's local project workflow. 

## **11.14 Data Integrity Considerations** 

Because the current implementation uses local files and CSV records rather than a relational database, traditional database constraints are not being claimed. 

For example, the system does not claim SQL-level enforcement of: 

- Primary keys 

- Foreign keys 

- Referential integrity 

- Database transactions 

- Unique constraints 

Instead, application logic is responsible for maintaining consistency between profile identifiers, stored images, unknown IDs, and sighting records. 

This is an important architectural limitation. 

## **11.15 Profile and Sighting Relationship** 

The relationship between a registered Victim and its sightings is particularly important for N-ONE. Conceptually: 

Victim Profile │ │ Victim Found ↓ 

Victim Sighting │ ├── Timestamp ├── Location └── Profile ID 

If the same Victim is detected at another camera location, another logical sighting can be created. Therefore, the model supports the concept of a historical observation sequence: 

Victim │ ├── Sighting 1 

│      ├── Location A │      └── Time A │ ├── Sighting 2 │      ├── Location B │      └── Time B │ └── Sighting 3 ├── Location C └── Time C 

This is the basis for the location-aware Victim sighting history displayed by the application. 

## **11.16 Unknown Person and Re-ID Relationship** 

The Unknown Re-ID mechanism has a similar logical structure. 

Unknown Person │ ├── First Observation │ ├── Second Observation │ ├── Third Observation │ └── Latest Observation 

The Unknown Person record maintains summary information such as first and last observation, while the Unknown Sighting records represent individual observations. 

This provides two complementary levels of information: 

##### **Summary level** 

unknown_001 First seen: ... Last seen: ... Last location: ... 

##### **Sighting level** 

Sighting 1 → Time + Location Sighting 2 → Time + Location Sighting 3 → Time + Location 

## **11.17 Audit Record Relationship** 

Audit records provide a cross-cutting view of application activity. 

An audit event can logically reference: 

- User role 

- Operational mode 

- Subject 

- Event type 

- Time 

- Additional details 

For example: 

Operator │ ↓ Victim Search │ ↓ Victim Found │ ↓ 

Audit Record 

├── Timestamp ├── Mode ├── Subject ID ├── Role └── Details 

Similarly, a possible threat event can be represented through the same broad audit concept. 

## **11.18 Why a Logical ER Model Is Used** 

Although N-ONE does not currently use a relational database, the logical ER model remains useful for academic documentation. 

It helps explain: 

- What information the system manages 

- Which objects are related 

- How repeated observations are represented 

- How locations are associated with events 

- How user roles relate to operations 

- How profile information connects to recognition results 

It also provides a foundation for a possible future database migration. 

For example, if the system were later expanded into a database-backed deployment, the logical entities could potentially be mapped into database tables. Such a migration is **not part of the current implementation** and should therefore be treated as future architectural work rather than an existing feature. 

## **11.19 Current Model vs. Future Database Model** 

**Aspect Current N-ONE Possible Future Extension** 

|User session|Streamlit session state|Centralized session/auth service|
|---|---|---|
|Profiles|Image files + metadata|Profile database|
|Unknown persons|CSV + image files|Database-backed entity|
|Sightings|CSV records|Relational/NoSQL event store|
|Camera context|Runtime/event information|Camera inventory database|
|Audit records|Local application logs|Centralized audit database|
|Referential integrity|Application logic|Database constraints|
|Multi-user persistence|Local/file-based|Centralized storage|



The future column represents an architectural possibility, not an implemented component. 

## **11.20 Limitations of the Logical Data Model** 

The current logical model has several limitations that should be clearly documented. 

#### **No SQL implementation** 

The project does not currently create SQL tables for these entities. 

#### **No database-enforced relationships** 

Relationships are conceptual/application-level relationships rather than database-enforced foreign keys. 

#### **File-based persistence** 

Images and CSV files form the primary persistent data layer. 

#### **Limited scalability** 

A file-based architecture may become increasingly difficult to manage as the number of users, cameras, profiles, and events increases. 

#### **No claim of centralized storage** 

The current design does not establish a centralized multi-server data store. 

#### **Application-level consistency** 

Consistency between profile images, metadata, and log records depends on application behavior rather than database transaction mechanisms. 

## **11.21 Summary** 

The N-ONE logical ER/data model describes seven major information entities: **User Session, Profile, Unknown Person, Unknown Sighting, Victim Sighting, Audit Record, and Camera Context** . 

The Profile entity represents registered Staff and Victim information, while Victim Sighting represents target-specific observations. Unknown Person and Unknown Sighting provide the logical foundation for the local Unknown Re-ID workflow. Audit Records provide a broader event-oriented representation of application activity, while Camera Context associates observations with operatorentered locations. 

The model is intentionally described as a **logical data model rather than a physical database schema** . N-ONE currently uses Streamlit session state, local image directories, and CSV-based persistence instead of SQL tables and database-enforced relationships. 

This distinction keeps the academic report consistent with the actual implementation while still providing a clear representation of the system's data structure and relationships. 

## **CHAPTER 12 – PROJECT EXPLANATION** 

This chapter explains the operational workflow of N-ONE from application startup to authentication, profile enrollment, camera processing, Victim Search, Staff Recognition, Unknown Re-ID, Threat Detection, browser-based WebRTC processing, and error handling. 

The project follows a mode-dependent processing architecture. Although the different modes are accessible through the same Streamlit dashboard, their internal processing behavior is not identical. In particular, the stateful OpenCV processing path and the browser WebRTC path have different handling of UI state, logging, and frame processing. 

### **12.1 Application Startup** 

The execution of N-ONE begins through the application's main() function. 

During startup, the application performs the basic initialization required for normal operation. 

The major startup operations are: 

1. Initialize required directories. 

2. Initialize or prepare log files. 

3. Set default Streamlit session-state values. 

4. Render the sidebar. 

5. Load authentication-related configuration. 

6. Load known profile encodings for authenticated sessions. 

7. Render the main dashboard. 

8. Render analytics-related panels. 

9. Render the log viewer. 

The simplified startup sequence is: 

Application Start ↓ main() ↓ Initialize Directories ↓ Initialize Logs ↓ Set Session Defaults ↓ Load Authentication Configuration ↓ Authentication Check ↓ Authenticated? /       \ No         Yes ↓           ↓ Locked /     Load Known Login UI     Encodings ↓ Render Dashboard ↓ Analytics + Logs 

If the required credentials are unavailable, the application does not proceed into normal authenticated operation. 

This provides an initial configuration boundary before the user can access the main dashboard. 

## **12.2 Authentication** 

Authentication is performed through the application's sidebar. 

The Administrator or Operator enters a username and password. N-ONE obtains the configured credentials from either: 

- Process environment variables 

- Streamlit Secrets 

The application then compares the submitted values with the configured credentials. 

The process can be represented as: 

Username + Password ↓ Read configured credentials ↓ Compare credentials ↓ Valid? /       \ Yes        No ↓          ↓ Assign      Increment role        failure count ↓           ↓ Set        5 failures? authenticated     / \ ↓            No  Yes Rerun page       ↓    ↓ ↓          Continue 60-sec lock Role-based dashboard 

The two primary roles are: 

#### **Administrator** 

The Administrator receives access to management-oriented operations such as: 

- Profile registration 

- Model configuration 

- Profile management 

- Administrative controls 

#### **Operator** 

The Operator receives access to operational functionality such as: 

- Monitoring 

- Victim Search 

- Staff/attendance 

- Result review 

- Log review 

### **12.2.1 Login Failure Protection** 

N-ONE includes a login-failure protection mechanism. 

The current configuration permits: 

Maximum failed attempts = 5 Lockout duration        = 60 seconds 

After five unsuccessful attempts, the session is locked for 60 seconds. 

This mechanism is an application-level protection measure. It should not be described as a complete enterprise identity-management system. 

### **12.2.2 Logout** 

When the user logs out, the application clears the authentication and role-related session state. 

The user is then returned to the unauthenticated state and must authenticate again to access protected functionality. 

The conceptual flow is: 

Authenticated Session ↓ 

Logout ↓ 

Clear authentication and role state ↓ Unauthenticated UI 

## **12.3 Profile Enrollment** 

Profile enrollment is the process through which an Administrator creates a registered Staff or Victim profile. 

The input can originate from an uploaded image or the guided multi-angle capture workflow. 

The image-processing sequence begins by reading the registration image using Pillow. The image is then converted into the format required by the computer-vision backend. Registration Image ↓ Pillow ↓ Image Decode ↓ BGR Conversion ↓ Loaded Face Backend ↓ Face Detection 

The backend then searches for face regions. 

### **12.3.1 Single-Face Validation** 

The registration workflow requires **exactly one detected face** . 

The decision process is: 

Face Detection ↓ Number of detected faces ↓ Exactly 1? /       \ No         Yes ↓           ↓ Reject      Continue registration ↓ 

Validate face size 

This prevents a registration image containing multiple people from being directly used as an unambiguous profile reference. 

### **12.3.2 Face Crop and Padding** 

After successful validation, the detected face region is cropped. 

The crop receives approximately **25% padding** around the detected face region. 

Original Image ↓ Face Region ↓ 25% Padding ↓ Face Crop ↓ Save Profile 

The resulting image is stored in the registered-profile directory. 

The naming convention distinguishes Staff and Victim profiles: 

Staff_<profile_id>.jpg Victim_<profile_id>.jpg 

### **12.3.3 Guided Multi-Angle Enrollment** 

The guided registration workflow associates multiple views with one profile ID. The expected angles are: 

Front Left Right Up Down 

The logical structure is: 

Profile ID │ ┌───────────┼───────────┐ ↓           ↓           ↓ Front       Left        Right │           │           │ └───────────┼───────────┘ │ Up / Down │ ↓ Registered Profile 

Existing angle files associated with the same profile ID can be replaced during an update. 

This provides a controlled reference set for subsequent face comparison. 

## **12.4 Victim Search** 

Victim Search is one of the central operational workflows of N-ONE. 

The operator selects: 

1. Lost Person Search 

The operator then: 

1. Selects one registered Victim. 

2. Enters the camera location. 

3. Selects a camera/video source. 

4. Starts surveillance. 

The workflow can be represented as: 

Operator ↓ 

Select "Lost Person Search" ↓ Select Victim ↓ Enter Camera Location ↓ Select Source ↓ Start Surveillance ↓ Process Frames 

### **12.4.1 Stateful OpenCV Processing** 

In the stateful OpenCV path, frames are processed continuously by the application's processing loop. 

The general process is: 

Frame ↓ Face Detection ↓ Face Representation 

↓ 

Selected Victim Cache ↓ 

Comparison ↓ 

Distance ↓ Threshold ↓ 

Match / No Match 

The candidate cache is restricted to the selected Victim profile in the neural recognition path. 

This target restriction is important because the purpose of Victim Search is not to perform unrestricted identification across every registered profile. 

### **12.4.2 Victim Match** 

When a genuine target match satisfies the configured matching condition, the application generates a **Victim Found** event. 

The result can contain: 

- Victim profile image 

- Profile ID 

- Camera location 

- Recognition distance 

- Timestamp 

- Active model 

- Backend 

- Distance metric 

- Latest sighting information by location 

The result is presented through a dedicated result card. 

The logical flow is: 

Selected Victim ↓ Detected Face ↓ Embedding Comparison ↓ Distance ≤ Threshold ↓ 

Victim Found ↓ 

Create Event 

↓ Store Sighting ↓ Display Result Card 

### **12.4.3 Victim Non-Match** 

When the detected face does not satisfy the configured target-matching condition, N-ONE does not assign the selected Victim identity. 

This is important because a non-match must not be converted into a positive Victim identification merely because a Victim Search operation is active. 

Therefore: 

Face ↓ Comparison ↓ Threshold Not Satisfied ↓ No Victim Match 

The system continues processing subsequent frames. 

### **12.4.4 OpenCV Fallback Boundary** 

When the complete neural runtime is unavailable, N-ONE uses the OpenCV fallback path. 

In this condition, the application does not present the fallback as equivalent to the full neural identity-recognition system. 

The Victim Search interface can indicate that face detection is occurring while identity matching requires the appropriate neural runtime. 

This creates an explicit safety boundary: 

Victim Search ↓ 

Neural Runtime Available? /            \ Yes             No ↓               ↓ Neural matching   OpenCV fallback ↓               ↓ 

Threshold         Face detection / decision           fallback features ↓               ↓ Victim result     Identity matching requires neural runtime 

This prevents unsupported Victim identity claims from being generated by the fallback path. 

## **12.5 Staff Recognition / Attendance** 

The Staff Recognition/Attendance mode uses a broader known-profile cache than Victim Search. 

In this mode, detected faces can be compared with the registered profiles available to the attendance workflow. 

The general process is: 

Camera Frame ↓ Face Detection ↓ Face Representation ↓ Known Profile Cache ↓ Compare Candidates ↓ Match? /      \ Yes       No ↓         ↓ Known     Unknown Staff     Workflow Result 

If a registered Staff profile satisfies the configured matching condition, the corresponding known identity can be displayed. 

If no registered identity is found, the system proceeds to the Unknown Re-ID process. 

### **12.5.1 Unknown Handling During Attendance** 

When no known Staff/profile match is obtained: 

No Known Match ↓ Check Unknown Cache ↓ Existing Unknown? /          \ Yes           No ↓             ↓ Existing       Create Unknown ID     New ID ↓             ↓ Update         Save Crop History        + Metadata 

This allows the attendance workflow to distinguish between: 

- Previously observed unknown individuals 

- Newly observed unknown individuals 

### **12.5.2 Staff Evaluation Boundary** 

The current repository does not contain an independent Staff benchmark equivalent to the Victim benchmark. 

Therefore, the Victim benchmark results must **not** be reused as Staff recognition accuracy. 

The current documented status is: 

##### **Staff-specific recognition accuracy: Not measured in the current implementation/evaluation.** 

This distinction is important for maintaining the technical validity of the report. 

## **12.6 Unknown Re-ID** 

Unknown Re-ID allows N-ONE to associate repeated observations with a locally generated unknown identifier. 

When a person cannot be matched with the known profile cache, the system checks the unknown cache. 

A new unknown can receive an identifier such as: 

unknown_001 unknown_002 unknown_003 

The face crop and associated metadata are saved. 

### **12.6.1 Unknown Reference** 

The stored unknown image can subsequently act as a reference representation for future comparisons. 

The process is: 

New Unknown ↓ Save Face Crop ↓ Create Representation ↓ Store Unknown Record ↓ Future Face ↓ Compare with Unknown Cache 

If a later face sufficiently matches an existing unknown representation, the system associates the observation with that existing unknown ID. 

### **12.6.2 Updating Unknown Information** 

When an existing unknown is re-identified, information such as: 

- Last timestamp 

- Last location 

- Sighting history 

can be updated. 

A new sighting record can also be appended, subject to the implemented write-throttling rule. 

The simplified workflow is: 

Existing Unknown Match ↓ Retrieve Unknown ID ↓ Update Last Timestamp ↓ Update Last Location 

↓ 

Append Sighting 

The system therefore provides local observation continuity. 

However, unknown_001 remains an **application-generated identifier** . It does not establish the person's legal or real-world identity. 

## **12.7 Threat Detection** 

Threat Detection is implemented as a separate operational mode. 

When threat mode is active, the application executes check_weapon_contours() and returns through the threat-processing path before entering normal face processing. 

This separation prevents face-recognition models from being incorrectly represented as weapondetection models. 

The threat-processing sequence is approximately: 

Camera Frame ↓ check_weapon_contours() ↓ Edge Detection ↓ Contour Extraction ↓ Geometric Filtering ↓ Possible Weapon? ↓ Warm HSV Analysis ↓ Possible Fire? ↓ Alert Result 

### **12.7.1 Contour-Based Analysis** 

The contour-based path evaluates visual structures using characteristics such as: 

- Area 

- Aspect ratio 

- Fill ratio 

##### ● Solidity 

The purpose is to identify shapes that satisfy the implemented heuristic conditions. 

This does not establish that an object is definitively a weapon. 

### **12.7.2 Warm-Colour Analysis** 

A separate HSV-based process searches for saturated warm-colour regions. 

This provides an additional heuristic path for possible fire-like regions. 

The result can therefore include: 

Possible weapon Possible fire No threat 

The wording **possible** is important because the implementation is heuristic rather than a verified deep-learning classifier. 

### **12.7.3 Separation from Face Recognition** 

Threat Detection does not use: 

- FaceNet 

- FaceNet512 

- ArcFace 

- Face-recognition cosine threshold 

The processing paths are therefore: 

Camera Frame │ ┌─────────┴─────────┐ ↓                   ↓ Face Recognition      Threat Detection │                   │ Face Detection       Canny / Contours │                   │ Embedding             HSV Analysis │                   │ Distance              Heuristic │                   │ Known/Unknown        Possible Alert 

## **12.8 Browser WebRTC Path** 

N-ONE also supports an optional browser-based camera path using WebRTC. 

This path differs from the stateful OpenCV loop in how frame processing communicates with the Streamlit interface. 

The browser camera provides frames to a worker-thread processor. 

Browser Camera ↓ WebRTC ↓ Worker-Thread Processor ↓ Frame Annotation ↓ Protected Status Object ↓ Streamlit UI Polling ↓ Display Result 

### **12.8.1 Worker-Thread Processing** 

The WebRTC callback is designed primarily for frame processing and annotation. 

It deliberately avoids performing certain Streamlit-side operations directly inside the worker callback. 

In particular, the callback does not directly perform: 

- Streamlit session-state writes 

- CSV logging 

- Disk writes 

This separation is important because the WebRTC callback operates in a worker-thread context. 

### **12.8.2 Protected Status Object** 

The latest selected-Victim result can be placed into a protected status object. 

The Streamlit UI then polls this status information and updates the visible interface. 

The architecture can therefore be represented as: 

WebRTC Worker 

↓ 

Process Frame 

↓ 

Update Protected Status 

↓ 

Streamlit UI Polling 

↓ 

Update Visible Result 

This differs from the stateful OpenCV loop, where processing and application state handling occur within the main application workflow. 

### **12.8.3 Academic Demonstration Consideration** 

Because the two camera paths do not operate identically, an academic demonstration should clearly state which processing path is being demonstrated. 

For example: 

OpenCV path → stateful processing + local logging 

WebRTC path 

→ worker-thread annotation + UI polling 

This distinction avoids presenting the two paths as technically identical. 

## **12.9 Error Handling** 

N-ONE contains several defensive checks designed to prevent common runtime problems from terminating the entire workflow. 

The application handles conditions including: 

- Missing optional WebRTC imports 

- Missing authentication secrets 

- Invalid image files 

- No-face registration images 

- Multiple-face registration images 

- Black or invalid frames 

- Unavailable camera sources 

- Missing files 

- CSV parsing failures 

- Backend exceptions 

### **12.9.1 Missing Credentials** 

If the required authentication credentials are missing, the application does not allow normal dashboard access. 

Credentials Missing ↓ Configuration Error ↓ 

Dashboard Remains Locked 

This is preferable to silently operating with undefined authentication configuration. 

### **12.9.2 Invalid Registration Image** 

If an uploaded image cannot be decoded or processed, the registration process reports the problem rather than creating an invalid profile. 

Similarly, images containing zero or multiple detected faces do not satisfy the normal single-face enrollment condition. 

Uploaded Image ↓ Decode ↓ Valid? /    \ No      Yes ↓        ↓ Error   Face Detection 

### **12.9.3 Camera Errors** 

Camera availability can vary depending on: 

- Camera index 

- Operating-system backend 

- Device availability 

- Stream accessibility 

- Browser permissions 

- Network conditions 

The application therefore includes handling for unavailable or invalid camera sources. 

### **12.9.4 CSV Errors** 

Because CSV files are part of the persistence layer, malformed or unavailable files can produce parsing or file-access errors. 

The application contains defensive handling for CSV-related failures so that the dashboard can handle such conditions without assuming that the data source is always valid. 

### **12.9.5 Backend Exceptions** 

The face-processing backend may encounter exceptions when optional dependencies are unavailable or when an unexpected processing condition occurs. 

N-ONE contains handling around backend operations to prevent an isolated backend failure from automatically being interpreted as a valid recognition result. 

## **12.10 Optional Analytics and Capability Boundaries** 

Some application components include hooks or helper interfaces for additional face-analysis capabilities. 

These can include: 

- Face attributes 

- Face extraction 

- One-to-one verification 

- Anti-spoofing/liveness-related operations 

However, a fallback result from an unavailable backend must not be described as successful inference. 

For example, if the required backend is unavailable, returning a fallback or unavailable status does **not** mean that the application successfully performed: 

- Liveness detection 

- Attribute classification 

- Anti-spoofing 

- Neural face analysis 

Therefore, the report distinguishes between an **implemented interface/hook** and an **actively verified AI capability** . 

## **12.11 Complete Operational Workflow** 

The complete N-ONE operational workflow can be summarized as: 

START ↓ Initialize Application ↓ Authentication / RBAC ↓ Role Identified ↓ Dashboard ↓ Select Operational Mode ↓ Select Data Source ↓ Frames ↓ ┌─────────┼────────────┐ ↓         ↓            ↓ Victim      Staff       Threat Search      /Attend.    Detection ↓         ↓            ↓ Face        Face         CV Heuristic Processing  Processing   Processing ↓         ↓            ↓ Target      Known/       Possible Match       Unknown      Alert ↓         ↓            ↓ Victim      Unknown      Alert/ Found       Re-ID        Log │         │            │ └─────────┼────────────┘ ↓ Local Storage ↓ Dashboard Review ↓ Human Review 

This workflow demonstrates that N-ONE is not simply a face-recognition program. It is an integrated application containing several processing modes and supporting data-management functions. 

## **12.12 Operational Separation of Major Modes** 

The three major operational paths can be summarized as follows: 

|**Mode**|**Primary Input**|**Main Processing**|**Main Output**|
|---|---|---|---|
|Victim Search|Camera/video|Target-restricted face|Victim Found / No|
||frame|comparison|Match|
|Staff/|Camera/video|Known-profile recognition +|Known/Unknown|
|Attendance|frame|Unknown Re-ID|status|
|Threat|Camera/video|Contour + HSV heuristics|Possible weapon/fire|
|Detection|frame||alert|



This separation is important because the outputs have different meanings. 

A **Victim Found** event is a recognition result under the configured face-matching conditions. 

An **Unknown ID** is a locally generated re-identification label. 

A **Possible weapon/fire** event is a heuristic alert requiring human review. 

These three outputs should not be treated as equivalent forms of certainty. 

## **12.13 Project Execution Sequence** 

From an operator's perspective, the complete execution sequence can be described as: 

#### **Step 1 – Start application** 

The N-ONE Streamlit application is started and initializes its directories, session state, and logging environment. 

#### **Step 2 – Authenticate** 

The Administrator or Operator enters the configured credentials. 

#### **Step 3 – Access dashboard** 

The application loads the appropriate role-based dashboard. 

#### **Step 4 – Register profiles** 

If required, the Administrator registers Staff or Victim profiles. 

#### **Step 5 – Select mode** 

The Operator chooses Victim Search, Staff/Attendance, or Threat Detection. 

#### **Step 6 – Select camera/source** 

The operator chooses the appropriate camera, video, WebRTC source, or IP stream. 

#### **Step 7 – Process frames** 

The selected processing pipeline analyzes incoming frames. 

#### **Step 8 – Generate result** 

The system generates a recognition result, Unknown ID, or possible threat alert depending on the mode. 

#### **Step 9 – Store relevant information** 

The application updates the appropriate local files or CSV logs. 

#### **Step 10 – Review** 

The operator reviews the result through the dashboard. 

## **12.14 Important Implementation Boundaries** 

Several implementation boundaries should be explicitly maintained in the academic description. 

#### **Neural recognition vs fallback** 

The neural recognition path and OpenCV fallback are not equivalent implementations. 

#### **Victim benchmark vs Staff performance** 

Victim benchmark results must not be presented as Staff recognition accuracy. 

#### **Unknown Re-ID vs real identity** 

An Unknown ID is an application-level identifier, not proof of a person's identity. 

#### **Threat heuristic vs verified classification** 

A possible weapon/fire result is an alert, not a confirmed classification. 

#### **WebRTC vs OpenCV processing** 

The browser WebRTC worker-thread path and stateful OpenCV loop have different processing and logging behavior. 

#### **Optional hooks vs active capabilities** 

The existence of an interface for liveness or attributes does not establish that the feature is actively available in the audited runtime. 

## **12.15 Summary** 

The N-ONE project starts by initializing the application environment and establishing an authenticated session. Depending on the user's role, the system provides administrative or operational functionality. 

Profile enrollment creates controlled Staff and Victim reference images using single-face validation and padded face crops. During monitoring, the selected operational mode determines how incoming camera frames are processed. 

Victim Search restricts the recognition candidate set to the selected Victim when the neural runtime is available. Staff/Attendance uses the broader known-profile cache and can transition unmatched observations into the Unknown Re-ID workflow. Unknown Re-ID provides locally generated identifiers and repeated sighting history without claiming real-world identity. 

Threat Detection operates independently through contour and HSV-based heuristics and produces possible threat/fire alerts rather than verified classifications. 

The optional WebRTC path uses worker-thread frame processing and communicates results back to the Streamlit interface through protected status information, while the stateful OpenCV path has different state and logging behavior. 

Finally, N-ONE contains defensive handling for configuration, image, camera, CSV, and backend failures. These mechanisms improve operational robustness, while the report maintains clear boundaries between implemented functionality, conditional functionality, and capabilities that have not been experimentally established. 

## **CHAPTER 13 – CODING / IMPLEMENTATION** 

This chapter presents selected source-code excerpts from N-ONE to explain how important parts of the system are implemented. Instead of reproducing the complete app.py, only representative and technically significant sections are included. 

The selected listings demonstrate the implementation of: 

- Secure credential loading 

- Face-distance calculation 

- Target-restricted Victim matching 

- Registration validation 

- Threat-detection heuristics 

- Unknown-person registration and tracking 

- Current implementation limitations 

The code examples are intended to explain the implementation logic and its relationship with the system architecture described in previous chapters. 

### **13.1 Authentication Secret Loading** 

**File:** app.py **Functions:** _read_secret() and load_auth_credentials() **Purpose:** Load authentication credentials from configuration sources without hardcoding them in the application. 

A representative implementation is: 

def _read_secret(name: str) -> str | None: environment_value = os.getenv(name) if environment_value is not None: return environment_value 

try: secret_value = st.secrets.get(name) except StreamlitSecretNotFoundError: return None 

return None if secret_value is None else str(secret_value) 

#### **Explanation** 

The function accepts the name of a configuration value and attempts to retrieve it from the process environment. 

The first source checked is: 

os.getenv(name) 

This allows credentials to be supplied through environment variables rather than being embedded directly into the source code. 

If the environment variable is unavailable, the function attempts to read the value from Streamlit Secrets: 

st.secrets.get(name) 

If Streamlit Secrets are unavailable, the function returns: 

None 

The function therefore does not generate a default username or password when the configuration is missing. 

#### **Authentication configuration flow** 

Requested Secret ↓ Environment Variable 

↓ 

Available? /       \ Yes        No ↓          ↓ Return     Streamlit Value      Secrets ↓ Available? /       \ Yes        No ↓          ↓ Return      Return Value        None 

The higher-level load_auth_credentials() function validates that the required Administrator and Operator credentials are actually present. 

If the configuration is incomplete, the application rejects the incomplete configuration rather than silently enabling a default login. 

This is important because a missing-secret condition should not result in an unauthenticated administrative interface. 

## **13.2 Face-Distance Calculation** 

The recognition system requires a numerical method for comparing a detected face representation with a stored reference representation. 

The representative implementation is: 

def calculate_face_distance( 

face_encoding, reference_encoding, metric="cosine" ): probe = np.asarray(face_encoding, dtype=np.float64) reference = np.asarray(reference_encoding, dtype=np.float64) 

if probe.shape != reference.shape: raise ValueError("Face embedding dimensions do not match") 

if not np.all(np.isfinite(probe)) or not np.all(np.isfinite(reference)): raise ValueError("Face embedding contains non-finite values") 

if metric == "euclidean": 

return float(np.linalg.norm(probe - reference)) 

if metric == "euclidean_l2": return float( np.linalg.norm(probe - reference) / max( np.linalg.norm(probe) + np.linalg.norm(reference), 1e-8 ) ) return float( 1.0 - np.dot(probe, reference) / ( np.linalg.norm(probe) * np.linalg.norm(reference) ) ) 

### **13.2.1 Input Conversion** 

The function first converts both inputs into NumPy arrays: probe = np.asarray(face_encoding, dtype=np.float64) reference = np.asarray(reference_encoding, dtype=np.float64) 

Using a consistent numerical representation makes subsequent mathematical operations predictable. 

### **13.2.2 Dimension Validation** 

The two representations must have compatible dimensions. 

The implementation checks: if probe.shape != reference.shape: raise ValueError("Face embedding dimensions do not match") Without this check, the application could attempt to compare incompatible vectors. 

For example: Reference → [x1, x2, x3, ...] Probe     → [y1, y2, y3, ...] 

The dimensions must correspond before a direct distance calculation is performed. 

### **13.2.3 Finite-Value Validation** 

The function also verifies that the vectors contain finite numerical values: 

np.all(np.isfinite(probe)) 

np.all(np.isfinite(reference)) 

This prevents invalid numerical values such as NaN or infinite values from being silently used in the recognition calculation. 

### **13.2.4 Euclidean Distance** 

If the configured metric is euclidean, the implementation calculates: 

d(a,b)≠a∥−∥b d(a,b)≠\|a-b\| 

through: 

np.linalg.norm(probe - reference) 

A smaller Euclidean distance represents greater similarity. 

### **13.2.5 Normalized Euclidean Distance** 

The euclidean_l2 branch calculates a normalized form of the Euclidean distance. 

The denominator contains the magnitudes of the two vectors, with a small numerical safeguard: max(..., 1e-8) 

The purpose of this safeguard is to avoid an exact zero denominator. 

### **13.2.6 Cosine Distance** 

The default branch calculates cosine distance: 

dcos(a,b)≠1−⋅∥∥∥∥a b a b d_{cos}(a,b) ≠ 1- \frac{a\cdot b} {\|a\|\|b\|} 

The implementation is: 

1.0 - np.dot(probe, reference) / ( 

np.linalg.norm(probe) * 

np.linalg.norm(reference) 

) 

N-ONE interprets a smaller distance as greater similarity. 

The resulting distance is subsequently evaluated against the configured matching threshold. 

### **13.2.7 Threshold Decision** 

Conceptually: 

Face Representation ↓ Distance Calculation ↓ Distance ≤ Threshold? 

/        \ Yes         No ↓           ↓ Potential      No Match Match 

The current source configuration uses a default threshold of 0.40 for the relevant recognition configuration. 

However, this threshold should be understood as a configuration value rather than a universal facerecognition standard. 

## **13.3 Target-Restricted Victim Matching** 

Victim Search uses a specific safeguard to restrict visible identity matching to the selected Victim. 

The representative source expression is: 

known_match = find_face_in_known_cache( face_encoding, match_threshold, profile_id=target_profile_id, role="Victim", metric=metric, ) if target_profile_id else None 

This code is significant because two restrictions are explicitly supplied: 

profile_id=target_profile_id role="Victim" 

The first identifies the specific profile selected for the search. 

The second restricts the search to the Victim category. 

### **13.3.1 Victim Search Logic** 

The logical flow is: 

Operator selects Victim ↓ target_profile_id ↓ Victim candidate restriction ↓ Face representation ↓ Distance comparison ↓ Threshold ↓ 

Match / No Match 

This differs from unrestricted attendance recognition, where the known cache can contain multiple registered profiles. 

### **13.3.2 Why the Restriction Matters** 

Suppose the system contains: 

Victim_A Victim_B Staff_A Staff_B 

During a search for Victim_A, the target-restricted branch is intended to evaluate the selected Victim rather than allowing an unrelated registered profile to satisfy the visible Victim result branch. 

The logical candidate set is therefore: 

All Registered Profiles ↓ 

Role = Victim ↓ Profile ID = Selected Victim ↓ Target Candidate 

This is one of the important implementation safeguards in the Victim Search workflow. 

## **13.4 Registration Validation** 

The profile-registration workflow validates the number of detected faces before creating a profile. A representative source excerpt is: 

regions = detect_face_regions(frame) 

if len(regions) == 0: return None, ( "No face detected. Face the camera directly " "with good lighting." ) 

if len(regions) > 1: return None, ( "Multiple faces detected. Keep only one " "person in the frame." ) 

### **13.4.1 No Face Condition** 

If the detector returns no face regions: 

len(regions) == 0 

the registration operation is rejected. 

This prevents the system from creating a profile without a usable face reference. 

### **13.4.2 Multiple Face Condition** 

If more than one face is detected: 

len(regions) > 1 

the registration is also rejected. 

This prevents ambiguity about which individual is being enrolled. 

### **13.4.3 Single-Face Condition** 

The accepted case is therefore: 

Number of detected faces = 1 

The processing can then continue to the crop-size check, padding operation, and profile persistence. 

### **13.4.4 Registration Processing** 

The broader registration flow is: 

Input Image ↓ Decode ↓ Face Detection ↓ Exactly One Face ↓ Minimum Face Size ↓ Face Crop ↓ 25% Padding ↓ Generate/Update Profile ID ↓ Save Profile Image 

This validation is particularly important for maintaining controlled enrollment data. 

## **13.5 Threat Heuristic Boundary** 

N-ONE's Threat Detection path uses a heuristic contour-analysis process rather than a neural weapon-recognition model. 

A representative condition is: 

if ( 

aspect_ratio >= 2.5 and fill_ratio >= 0.08 and solidity >= 0.15 ): 

boxes.append((x, y, w, h, "Possible weapon")) 

Three geometric characteristics are used in this condition: 

- Aspect ratio 

- Fill ratio 

- Solidity 

### **13.5.1 Aspect Ratio** 

Aspect ratio describes the relationship between the width and height of the detected contour. Conceptually: 

AspectRatio=widthheightAspectRatio=\frac{width}{height} 

The implemented threshold checks whether the value is at least: 

2.5 

### **13.5.2 Fill Ratio** 

Fill ratio represents the relationship between the contour area and its enclosing bounding region. The implementation uses a threshold of: 

- 0.08 

as part of the heuristic condition. 

### **13.5.3 Solidity** 

Solidity is another geometric characteristic used by the heuristic. 

The current condition requires: 

solidity >= 0.15 

when generating the corresponding possible-weapon box. 

### **13.5.4 Important Interpretation Boundary** 

The generated label is deliberately: 

Possible weapon 

and not: 

Weapon confirmed 

The source documentation explicitly recognizes that contour analysis cannot prove that an object is a gun, knife, or another specific weapon. 

Therefore, the report must retain the word **Possible** when describing this output. 

The processing is better understood as: 

Visual Pattern ↓ Geometric Heuristic ↓ Possible Weapon Alert ↓ Human Review rather than: Object ↓ AI Weapon Classifier ↓ Confirmed Weapon 

## **13.6 Unknown Registration** 

The Unknown Re-ID workflow creates a new local identifier when a detected face cannot be associated with an existing known profile or existing unknown record. 

The register_new_unknown() operation performs several related tasks. 

Conceptually: 

New Unknown Face ↓ Generate Sequential ID ↓ Save Face Crop ↓ 

Add Unknown Database Row ↓ Add First Sighting ↓ Write Audit Event An identifier may take the form: 

unknown_001 unknown_002 unknown_003 

The sequential ID provides a stable application-level reference for subsequent observations. 

### **13.6.1 Unknown Image** 

The detected face crop is saved as the visual reference associated with the newly created unknown. 

This allows later observations to be compared with the stored unknown representation. 

### **13.6.2 Unknown Database** 

The new record is added to the unknown-person database: 

unknown_person_db.csv 

The stored information can include the application's unknown-person metadata. 

### **13.6.3 First Sighting** 

The first observation is also recorded in the unknown-sighting log. 

This establishes the initial observation time and location. 

### **13.6.4 Audit Event** 

The creation of the unknown can also generate an audit event, allowing the application to maintain an operational history. 

## **13.7 Updating Unknown Sightings** 

When a later observation is associated with an existing unknown ID, update_unknown_sighting() updates the corresponding last-known information. 

The logical sequence is: 

Detected Face ↓ Unknown Cache Comparison ↓ Existing Unknown Match ↓ Retrieve Unknown ID ↓ Update Last Timestamp ↓ Update Last Location ↓ Append Sighting Record 

A short duplicate-write interval is applied to reduce unnecessary repeated records for the same ID/location combination. 

This allows the system to maintain a useful sighting history without generating an excessive number of identical records during continuous observation. 

## **13.8 Code-to-Architecture Mapping** 

The selected code listings correspond directly to the modules described in earlier chapters. 

|**Code Component**|**Architectural Module**|**Purpose**|
|---|---|---|
|_read_secret()|Authentication/RBAC|Secure configuration loading|
|load_auth_credentia<br>ls()|Authentication/RBAC|Credential validation|
|calculate_face_dist<br>ance()|Face Recognition|Representation comparison|
|find_face_in_known_<br>cache()|Recognition/Victim Search|Candidate matching|



detect_face_regions Registration/Recognition Face detection () Contour heuristic Threat Detection Possible threat identification register_new_unknow Unknown Re-ID New unknown creation n() update_unknown_sigh Unknown Re-ID Repeat observation tracking ting() 

This mapping demonstrates that the code is not presented as isolated snippets; each listing represents an actual functional component of the N-ONE architecture. 

## **13.9 Example of the Recognition Decision Pipeline** 

The important recognition functions can be conceptually combined as follows: 

Camera Frame ↓ detect_face_regions() ↓ Face Region ↓ Face Representation ↓ find_face_in_known_cache() ↓ calculate_face_distance() ↓ Threshold Comparison ↓ Known / No Match For Victim Search, the matching call additionally receives: profile_id = target_profile_id role       = "Victim" 

This creates the target-restricted behavior described in Chapter 12. 

## **13.10 Example of Registration Decision Pipeline** 

The registration-related code can similarly be represented as: 

Uploaded / Captured Image ↓ Image Decode ↓ detect_face_regions() ↓ Face Count /       \ 0        >1 ↓         ↓ Reject     Reject \       / \     / Exactly 1 ↓ Size Check ↓ Face Crop ↓ Padding ↓ Save Profile 

This demonstrates how source-level validation corresponds to the application's functional requirement of controlled enrollment. 

## **13.11 Implementation Architecture** 

The current implementation is largely concentrated in the main application module. 

The monolithic structure has an important advantage for a university prototype: the application can be executed without coordinating several independent services. 

The simplified architecture is: 

┌────────────────────────────────────┐ │              app.py                │ │                                    │ │ Authentication                     │ │ Registration                       │ │ Camera Processing                  │ 

│ Face Recognition                   │ │ Victim Search                      │ │ Unknown Re-ID                      │ │ Threat Detection                   │ │ Dashboard                          │ │ Logging                            │ └───────────────┬────────────────────┘ ↓ 

Local Files / CSV 

This is straightforward to run and understand, but it also concentrates several responsibilities in one application module. 

## **13.12 Implementation Limitations** 

The current implementation has several architectural limitations that should be explicitly documented. 

### **13.12.1 Single-module concentration** 

The prototype concentrates UI, storage, and processing responsibilities in app.py. 

This simplifies execution but increases coupling between different parts of the application. 

A larger system could separate responsibilities into modules or services such as: 

Authentication Recognition Threat Detection Storage Camera Service API Layer Dashboard 

However, such a separation is not part of the current implementation. 

### **13.12.2 CSV concurrency** 

Direct CSV writes can create concurrency problems when multiple processes or workers attempt to modify the same file simultaneously. 

For example: 

Worker A ──┐ ├──→ CSV file 

Worker B ──┘ 

Without a database transaction or explicit file-locking architecture, concurrent writes can potentially create consistency problems. 

The current project does not add a database transaction layer. 

### **13.12.3 No Database Transaction Layer** 

The project does not currently implement: 

- SQL transactions 

- Database locking 

- Schema migration system 

- Database-level referential integrity 

The application instead relies on its local file and CSV persistence logic. 

### **13.12.4 No Encrypted Storage Wrapper** 

The current implementation does not add an encrypted storage wrapper around the locally stored profile images and CSV records. 

Therefore, sensitive data protection should also depend on appropriate operating-system and deployment-level access controls. 

The report should not claim that the stored face images or CSV files are encrypted unless that functionality is separately implemented and verified. 

### **13.12.5 No Complete Service-Oriented Architecture** 

N-ONE is not currently implemented as a distributed microservice architecture. 

There is no established separation into: 

Authentication Service 

Recognition Service Threat Service Database Service API Gateway 

The project remains a monolithic application with internal functional boundaries. 

## **13.13 Security-Relevant Coding Practices** 

Several source-level practices contribute to safer implementation. 

#### **Configuration instead of hardcoded credentials** 

Credentials are obtained from environment variables or Streamlit Secrets. 

#### **Input validation** 

Registration images are checked for valid face counts. 

#### **Numerical validation** 

Face representations are checked for matching dimensions and finite values. 

#### **Explicit fallback boundary** 

The OpenCV fallback does not silently claim full neural identity-recognition capability. 

#### **Conservative threat terminology** 

The contour-based result uses: 

Possible weapon 

rather than claiming confirmed classification. 

#### **Target restriction** 

Victim Search passes the selected profile ID and Victim role to the known-cache matching function. 

These practices help ensure that the software behavior remains aligned with the documented system boundaries. 

## **13.14 Implementation vs. Claimed Capability** 

The source code also demonstrates why the report must distinguish between what is implemented and what is experimentally established. 

For example: 

|**Capability**|**Source-Level Status**|**Performance/Effectiveness Status**|
|---|---|---|
|Credential loading|Implemented|Configuration-dependent|
|Face-distance<br>calculation|Implemented|Depends on representation/backend|



|Victim candidate<br>restriction|Implemented|Requires appropriate neural runtime for<br>identity matching|
|---|---|---|
|Single-face<br>enrollment validation|Implemented|Operational behavior|
|Unknown ID creation|Implemented|Unknown Re-ID accuracy not established|
|Contour threat<br>heuristic|Implemented|Not a verified weapon classifier|
|Staff recognition|Implemented<br>workflow|Accuracy not measured|
|Neural model<br>evaluation|Separate evaluation<br>workspace|Benchmark-specific results|



This distinction prevents source-code presence from being interpreted as proof of a particular realworld performance level. 

## **13.15 Summary** 

The N-ONE implementation uses focused functions to implement its main security, recognition, registration, threat-analysis, and Unknown Re-ID workflows. 

The _read_secret() and load_auth_credentials() functions provide configurationbased authentication rather than embedding credentials in the source. The calculate_face_distance() function performs validated numerical comparison using configurable distance metrics, with cosine distance forming the relevant default path. 

Victim Search uses target-specific profile_id and role="Victim" filters to restrict the visible identity-matching branch to the selected target. Registration validates that exactly one face is present before creating a padded face crop. 

The threat-detection implementation uses geometric contour heuristics and deliberately produces a **Possible weapon** result rather than a confirmed weapon classification. Unknown Re-ID creates sequential local identifiers, stores reference crops, and maintains subsequent sighting information. 

Finally, the current single-module architecture is appropriate for the project's prototype scope but has limitations involving code concentration, concurrent CSV access, absence of database transactions, lack of a schema-migration mechanism, and absence of an encrypted storage wrapper. These limitations should remain explicitly documented rather than being presented as capabilities that the current implementation does not provide. 

## **CHAPTER 14 – RESULT AND ANALYSIS** 

This chapter presents the experimental results obtained from the N-ONE evaluation workspace. The primary focus of the benchmark is **Victim Face Recognition** , with particular attention to model comparison, threshold behavior, false Victim matches, and inference performance. 

The evaluation is deliberately separated from the live production configuration. Therefore, the measured benchmark results are reported as experimental evidence under the specified dataset and test protocol rather than as universal claims about the complete N-ONE system. 

### **14.1 Evaluation Protocol** 

The evaluation separates the images used for **Victim enrollment** from those used for **Victim testing** . This separation is important because using the same image for both enrollment and testing could produce an unrealistically favorable result. 

The benchmark contains: 

- **5 Victim identities** 

- **11 Victim enrollment images** 

- **32 genuine Victim test images** 

- **10 impostor identities represented by 12 images** 

- **60 negative trials** 

A **genuine trial** represents a test image belonging to the target Victim. 

An **impostor trial** represents an image belonging to another person that is tested against the selected Victim identity. 

The benchmark uses: 

Detector       = RetinaFace where supported Distance       = Cosine Threshold range = 0.20 – 0.60 

For a given Victim, the test face is compared against the available enrollment representations for that target. The minimum distance is used for the decision. 

The decision rule can be expressed as: 

dmin τd_{\min} \leq \tau≤ 

where: 

- dmin d_{\min} = minimum distance between the test representation and the target's enrollment representations 

- τ\tau = selected threshold 

If the minimum distance is less than or equal to the threshold, the trial is accepted as a match. 

### **14.1.1 Genuine and Impostor Trials** 

The benchmark distinguishes two fundamental types of trials. 

#### **Genuine trial** 

A genuine trial uses an image of the actual target Victim. 

Target Victim ↓ Test Image ↓ Compare with Target Enrollment ↓ Distance ↓ Threshold ↓ Accept / Reject 

A genuine test that is correctly accepted contributes to **True Positive (TP)** . 

A genuine test that is incorrectly rejected contributes to **False Negative (FN)** . 

#### **Impostor trial** 

An impostor trial uses an image of another person. 

Different Person ↓ Impostor Image ↓ Compare with Target Victim ↓ Distance ↓ Threshold ↓ Accept / Reject 

If an impostor is incorrectly accepted as the Victim, it becomes a **False Positive (FP)** . 

If an impostor is correctly rejected, it contributes to **True Negative (TN)** . 

This distinction is particularly important for Victim Search because a false Victim identification is a more significant error than simply failing to recognize a genuine target. 

## **14.2 Threshold-0.40 Model Comparison** 

The following results were obtained at a threshold of **0.40** . 

|**Model**|**T**|**T**|**F**|**F**|**Precisi**|**Recall**|**F1**|**FAR**|**FRR**|**False**|
|---|---|---|---|---|---|---|---|---|---|---|
||**P**|**N**|**P**|**N**|**on**|||||**Victim**<br>**Matches**|
|FaceNet|21|60|0|11|1.0000|0.656|0.79245283|0.000|0.343|0|
|||||||25|02|0|75||
|FaceNet5|22|60|0|10|1.0000|0.687|0.81481481|0.000|0.312|0|
|12||||||50|48|0|50||
|ArcFace|23|60|0|9|1.0000|0.718|0.83636363|0.000|0.281|0|
|||||||75|64|0|25||



### **14.2.1 FaceNet** 

At threshold 0.40, FaceNet produced: 

- TP = 21 

- TN = 60 

- FP = 0 

- FN = 11 

The measured values were: 

Precision=1.0000Precision = 1.0000 Recall=0.65625Recall = 0.65625 F1=0.79245F1 = 0.79245 FAR=0FAR = 0 FRR=0.34375FRR = 0.34375 

There were **zero false Victim matches** in the available 60 negative trials. 

This means that within this benchmark protocol, no impostor trial was incorrectly accepted as the target at the 0.40 threshold. 

### **14.2.2 FaceNet512** 

FaceNet512 produced: 

- TP = 22 

- TN = 60 

- FP = 0 

- FN = 10 

The measured values were: 

Precision=1.0000Precision = 1.0000 Recall=0.68750Recall = 0.68750 F1=0.81481F1 = 0.81481 FAR=0FAR = 0 FRR=0.31250FRR = 0.31250 

Again, the benchmark recorded **zero false Victim matches** among the available negative trials. 

### **14.2.3 ArcFace** 

ArcFace produced: 

- TP = 23 

- TN = 60 

- FP = 0 

- FN = 9 

The measured values were: 

Precision=1.0000Precision = 1.0000 Recall=0.71875Recall = 0.71875 F1=0.83636F1 = 0.83636 FAR=0FAR = 0 FRR=0.28125FRR = 0.28125 

The benchmark therefore recorded **zero false Victim matches** among the 60 negative trials for ArcFace at the 0.40 threshold. 

Within this particular dataset and evaluation protocol, ArcFace produced the highest measured recall and F1 among the three tested configurations. 

This statement is strictly limited to the available benchmark. It does **not** establish universal recognition accuracy, a safety guarantee, or an automatic production recommendation. 

## **14.3 Understanding the Metrics** 

The evaluation uses standard classification metrics to describe recognition behavior. 

#### **True Positive** 

A genuine Victim is correctly accepted: 

TP=correct genuine acceptanceTP = \text{correct genuine acceptance} 

#### **True Negative** 

An impostor is correctly rejected: 

TN=correct impostor rejectionTN = \text{correct impostor rejection} 

#### **False Positive** 

An impostor is incorrectly accepted as the Victim: 

FP=incorrect Victim acceptanceFP = \text{incorrect Victim acceptance} 

#### **False Negative** 

A genuine Victim is incorrectly rejected: 

FN=missed genuine VictimFN = \text{missed genuine Victim} 

### **14.3.1 Precision** 

Precision measures how many accepted positive decisions were actually correct: Precision=TPTP+FPPrecision = \frac{TP}{TP+FP} 

For the three models at threshold 0.40, FP was zero, resulting in a measured precision of 1.0000. 

### **14.3.2 Recall** 

Recall measures the proportion of genuine Victim trials that were correctly accepted: Recall=TPTP+FNRecall = \frac{TP}{TP+FN} 

The measured recall values were: 

|**Model**|**Recall**|
|---|---|
|FaceNet|0.65625|
|FaceNet512|0.68750|
|ArcFace|0.71875|



These values indicate that some genuine Victim test images were not accepted at the selected threshold. 

### **14.3.3 F1 Score** 

F1 combines precision and recall: 

F1=2Precision×RecallPrecision+RecallF1 = 2 \frac{Precision \times Recall} {Precision+Recall} 

The measured F1 values were: 

**Model F1** 

FaceNet 0.79245 FaceNet512 0.81481 ArcFace 0.83636 

These values are benchmark-specific and should not be interpreted as universal model ratings. 

### **14.3.4 False Acceptance Rate** 

FAR represents the proportion of negative/impostor trials incorrectly accepted: FAR=FPFP+TNFAR = \frac{FP}{FP+TN} 

At threshold 0.40: 

FaceNet    → 0.0000 FaceNet512 → 0.0000 ArcFace    → 0.0000 

This means that no false Victim acceptance was observed in the available negative trials. 

However, **zero observed false positives is not proof that the true real-world FAR is zero** . The result is limited by the size and composition of the evaluated negative sample. 

### **14.3.5 False Rejection Rate** 

FRR represents genuine trials that were incorrectly rejected: 

FRR=FNTP+FNFRR = \frac{FN}{TP+FN} 

The measured values were: 

**Model FRR** FaceNet 0.34375 FaceNet512 0.31250 ArcFace 0.28125 

The results show that the benchmark still contains genuine Victim images that are rejected at the 0.40 threshold. 

## **14.4 Threshold Analysis** 

Threshold selection directly affects the balance between accepting genuine Victim images and rejecting impostors. 

A lower threshold generally requires greater similarity before accepting a match. A higher threshold makes acceptance less restrictive. 

The evaluation tested thresholds from: 

0.20 → 0.60 

At threshold 0.40, all three tested models recorded: 

False Positives = 0 

across the available 60 negative trials. 

However, when the threshold was relaxed, the observed false-positive behavior changed for some configurations. 

For example, FaceNet recorded: 

Threshold 0.50 → 1 FP Threshold 0.55 → 1 FP Threshold 0.60 → 2 FP 

This demonstrates the practical trade-off between threshold strictness and false acceptance. 

### **14.4.1 Threshold Trade-Off** 

The general relationship can be represented as: 

Lower Threshold ↓ More restrictive acceptance ↓ Potentially fewer false accepts ↓ Potentially more false rejects 

Higher Threshold 

↓ 

Less restrictive acceptance 

↓ 

Potentially more genuine accepts ↓ 

Potentially more false accepts 

The exact behavior is model-specific and must be measured rather than assumed. 

At threshold 0.60, FaceNet512 and ArcFace still recorded zero false positives in the available negative trials. However, this observation alone does not establish production superiority because model selection also depends on genuine acceptance, threshold calibration, deployment conditions, detector behavior, and representative test data. 

## **14.5 Performance Evidence** 

The benchmark performance file contains **55 image-level rows for each model** . 

The measured average inference latency was approximately: 

|**Model**|**Average Latency**|**Derived Average**<br>**FPS**|
|---|---|---|
|FaceNet|3.5909591327 s|0.2784771315|
|FaceNet512|3.9212489673 s|0.2550207876|
|ArcFace|3.8782448073 s|0.2578486015|



These values were obtained from the benchmark run and should be reported with their experimental context. 

### **14.5.1 FaceNet Performance** 

FaceNet recorded an average latency of approximately: 

3.5909591327 seconds3.5909591327\ seconds 

The corresponding derived average FPS was approximately: 

0.2784771315 FPS0.2784771315\ FPS 

### **14.5.2 FaceNet512 Performance** 

FaceNet512 recorded approximately: 

3.9212489673 seconds3.9212489673\ seconds 

average latency, corresponding to approximately: 

0.2550207876 FPS0.2550207876\ FPS 

### **14.5.3 ArcFace Performance** 

ArcFace recorded approximately: 

- 3.8782448073 seconds3.8782448073\ seconds 

average latency, corresponding to approximately: 

0.2578486015 FPS0.2578486015\ FPS 

### **14.5.4 Interpretation of Latency** 

The benchmark documentation indicates that the measured inference time includes processing components such as: 

- Face detection 

- Alignment/preprocessing 

- Embedding generation 

The benchmark did not use GPU acceleration. 

Therefore, these numbers should **not** be presented as the guaranteed FPS of the complete N-ONE application. 

For example, it would be incorrect to conclude: 

“N-ONE operates at 0.278 FPS.” 

The technically accurate statement is: 

“The benchmark run measured an average derived FPS of approximately 0.278 for the tested FaceNet configuration under the specified benchmark environment.” 

Application-level performance can differ because the complete application includes camera capture, frame handling, UI rendering, logging, storage operations, and other processing. 

## **14.6 Multi-Frame Evaluation** 

Multi-frame confirmation was considered as a potential extension of the Victim Search evaluation. 

The intended configurations were: 

- 1-frame confirmation 

- 3-frame confirmation 

- 5-frame confirmation 

However, the current evaluation evidence does not contain labeled video/frame sequences suitable for this experiment. 

The file: 

multi_frame_results.csv 

records: 

not_available 

for the tested model and frame-count combinations. 

Therefore: 

**Multi-frame 1/3/5 confirmation results are Not measured in the current implementation/evaluation.** 

### **14.6.1 Why No Accuracy Claim Is Made** 

Without labeled frame sequences, it is not possible to calculate meaningful sequence-level: 

- TP 

- TN 

- FP 

- FN 

- Confirmation latency 

- False Victim alert rate 

Therefore, the report does not claim that 3-frame or 5-frame confirmation improves recognition accuracy. 

A future experiment should use labeled video sequences and evaluate: 

Single frame 

vs. 

- 3-frame confirmation 

vs. 

- 5-frame confirmation 

using the same target and impostor definitions. 

## **14.7 Production Versus Benchmark Configuration** 

An important result of the evaluation process is that the experimental benchmark configuration is kept separate from the application's current source default. 

|**Mode**|**Model**|**Detector**|**Metric**|**Threshold**|**Status**|
|---|---|---|---|---|---|
|Victim<br>Search source<br>default|FaceNet|OpenCV|Cosine|0.40|Current source<br>default|
|Benchmark<br>comparison|FaceNet|RetinaFace|Cosine|0.40|Measured<br>benchmark<br>row|
|Benchmark<br>comparison|FaceNet512|RetinaFace|Cosine|0.40|Measured<br>benchmark<br>row|
|Benchmark<br>comparison|ArcFace|RetinaFace|Cosine|0.40|Benchmark<br>candidate|
|Staff<br>Recognition|Configured<br>model|Configured<br>detector|Configured<br>metric|Configured<br>threshold|Staff-specific<br>benchmark<br>unavailable|
|Unknown Re-<br>ID|Configured<br>model/fallback|Configured<br>detector|Configured<br>metric|Local<br>threshold<br>map|Accuracy<br>unavailable|
|Threat<br>Detection|Separate<br>heuristic|N/A|N/A|N/A|Face model is<br>not used|



This table is important because the benchmark and production environments are not identical. 

### **14.7.1 Production Configuration** 

The current Victim Search source default is: 

Model     = FaceNet Detector  = OpenCV Metric    = Cosine Threshold = 0.40 

This remains the documented source default. 

### **14.7.2 Benchmark Configuration** 

The benchmark comparison uses: 

Models: 

FaceNet FaceNet512 ArcFace 

Detector: 

RetinaFace where supported 

Metric: 

Cosine 

Threshold: 

0.40 

Consequently, the benchmark result for ArcFace, for example, should not be written as though the current production application is already operating with: 

##### ArcFace + RetinaFace 

The benchmark establishes experimental evidence for that configuration, not an automatic sourcecode change. 

## **14.8 Result Comparison** 

The measured threshold-0.40 results can be summarized as: 

|**Model**||**Genuine**<br>**Accepted**|**Genuine**<br>**Rejected**||**False Victim**<br>**Matches**|**Recall**|**F1**|
|---|---|---|---|---|---|---|---|
|FaceNet|21||11|0||0.6562<br>5|0.7924<br>5|
|FaceNet51|22||10|0||0.6875|0.8148|
|2||||||0|1|
|ArcFace|23||9|0||0.7187|0.8363|
|||||||5|6|



Within this particular benchmark, the number of correctly accepted genuine Victim trials increased from 21 for FaceNet to 22 for FaceNet512 and 23 for ArcFace, while all three configurations recorded zero false Victim matches in the 60 negative trials. 

These are **observed benchmark outcomes** , not universal model characteristics. 

## **14.9 False Victim Match Analysis** 

False Victim identification is an important error category for the N-ONE Victim Search workflow. 

At threshold 0.40, the benchmark recorded: 

FaceNet    → 0 false Victim matches FaceNet512 → 0 false Victim matches ArcFace    → 0 false Victim matches 

This means that none of the available negative trials was incorrectly accepted as the selected Victim at this threshold. 

However, the correct interpretation is: 

No false Victim match was observed in the evaluated negative trials. 

It should **not** be rewritten as: 

The system can never falsely identify another person as the Victim. 

The latter would require much broader evidence than the current dataset provides. 

## **14.10 Genuine Rejection Analysis** 

The benchmark also demonstrates that the system does not accept every genuine Victim test image. At threshold 0.40: 

FaceNet    → 11 FN FaceNet512 → 10 FN ArcFace    → 9 FN 

Therefore, the benchmark contains genuine appearances that were rejected by the recognition threshold. 

This can occur because face-recognition performance is affected by factors such as: 

- Pose 

- Illumination 

- Image quality 

- Face size 

- Occlusion 

- Detection quality 

- Difference between enrollment and test images 

The current benchmark demonstrates the existence of false negatives but does not establish which individual environmental factor caused each specific failure unless that condition has been separately labeled and analyzed. 

## **14.11 What the Benchmark Establishes** 

The current benchmark provides evidence for several specific observations. 

#### **1. Model comparison was performed** 

FaceNet, FaceNet512, and ArcFace were evaluated using the defined protocol. 

#### **2. Threshold 0.40 produced zero observed false Victim matches** 

All three models recorded: 

FP = 0 

in the available 60 negative trials. 

#### **3. Genuine acceptance differed between models** 

The measured TP counts were: 

FaceNet    = 21 FaceNet512 = 22 ArcFace    = 23 

#### **4. Genuine rejection was present** 

The measured FN counts were: 

FaceNet    = 11 FaceNet512 = 10 ArcFace    = 9 

#### **5. Performance differed between configurations** 

The benchmark recorded different average latency values for the three models. 

#### **6. Multi-frame performance remains unmeasured** 

No labeled sequence data were available for the planned 1/3/5-frame experiment. 

## **14.12 What the Benchmark Does Not Establish** 

The benchmark does **not** establish: 

- Universal face-recognition accuracy 

- Guaranteed Victim identification 

- Zero real-world false Victim matches 

- Production-level FPS 

- Staff recognition accuracy 

- Unknown Re-ID accuracy 

- Threat-detection accuracy 

- Multi-frame improvement 

- Performance on every camera type 

- Performance under every lighting condition 

- Large-scale multi-camera performance 

- Legal or regulatory compliance 

These boundaries are important because a small controlled benchmark cannot represent every deployment condition. 

## **14.13 Staff Recognition Result Status** 

Staff Recognition is implemented as an operational workflow, but an independent Staff benchmark is not available in the current evaluation evidence. 

Therefore, the report should use: 

##### **Staff-specific recognition accuracy: Not measured in the current implementation/evaluation.** 

The Victim benchmark values must not be copied into the Staff section because the datasets and evaluation objectives are different. 

This preserves the distinction between: 

Victim Benchmark 

≠! 

Staff Benchmark 

## **14.14 Unknown Re-ID Result Status** 

Unknown Re-ID is implemented as a local storage and repeated-observation workflow. 

However, the current evidence does not establish a validated Unknown Re-ID accuracy value. 

Therefore, metrics such as: 

- Unknown Re-ID precision 

- Unknown Re-ID recall 

- Unknown Re-ID F1 

- Unknown identity-switch rate 

should not be invented. 

The current documented status is: 

##### **Unknown Re-ID accuracy: Not measured.** 

## **14.15 Threat Detection Result Status** 

Threat Detection is implemented through a heuristic contour and HSV-processing path. 

The current Victim recognition benchmark does not evaluate its accuracy. 

Therefore, the face-recognition results cannot be used to claim: 

- Weapon-detection accuracy 

- Fire-detection accuracy 

- Precision/recall for threats 

- False alarm rate for threat detection 

The correct status is that Threat Detection is an implemented heuristic path whose effectiveness requires its own dedicated labeled evaluation. 

## **14.16 Overall Interpretation** 

The evaluation provides a controlled comparison of three face-representation configurations under a defined Victim recognition protocol. 

At threshold 0.40, all three tested models recorded zero observed false Victim matches in the available 60 negative trials. The genuine acceptance counts were 21 for FaceNet, 22 for FaceNet512, and 23 for ArcFace. Correspondingly, the measured recall values were 0.65625, 0.68750, and 0.71875. 

The benchmark also demonstrates the importance of threshold selection. Relaxing the threshold can change false-positive behavior, as demonstrated by the FaceNet threshold sweep. 

Performance measurements show that the tested neural configurations required several seconds per image in the recorded CPU benchmark environment. These measurements are benchmark-specific and should not be converted into guaranteed application FPS. 

The multi-frame experiment remains unavailable because labeled frame sequences were not present. Similarly, independent Staff, Unknown Re-ID, and Threat Detection accuracy measurements are not established by the current benchmark. 

## **14.17 Final Result Summary** 

The current evidence can be summarized as follows: 

|**Evaluation Area**|**Current Result**|
|---|---|
|Victim Face Recognition|Evaluated|
|FaceNet|Evaluated|
|FaceNet512|Evaluated|
|ArcFace|Evaluated|
|Threshold sweep|Evaluated|
|False Victim matches at 0.40|0 observed in 60 negative trials for all 3 models|
|Inference latency|Measured in benchmark|
|Derived FPS|Measured in benchmark|
|Multi-frame 1/3/5|Not measured|
|Staff recognition accuracy|Not measured|
|Unknown Re-ID accuracy|Not measured|
|Threat detection accuracy|Not measured|
|Production default|FaceNet + OpenCV + cosine + 0.40|



The most important conclusion is that the benchmark provides **evidence about the tested configurations under the specified dataset and protocol** , rather than a universal statement about N-ONE's performance in all environments. The repository also preserves the production default separately from the experimental benchmark configurations, allowing future model or threshold changes to be made only after additional validation. 

## **CHAPTER 15 – SOFTWARE TESTING** 

### **15.1 Introduction** 

Software testing is an essential stage in the development and validation of the N-ONE system. Since the project combines authentication, profile management, computer vision, face recognition, unknown-person tracking, browser-based video processing, local data storage, and AI model evaluation, testing cannot be limited to checking whether the application starts successfully. 

The testing process of N-ONE focuses primarily on **functional behavior, boundary conditions, data integrity, safety of identity assignment, and evaluation-workspace correctness** . 

Particular attention is given to the Victim Search subsystem because an incorrect identity assignment can be more significant than a simple recognition failure. The tests therefore verify that the system does not unnecessarily assign a Victim identity when the required recognition conditions are not satisfied. 

The current test strategy consists primarily of: 

- unit tests, 

- behavior tests, 

- boundary tests, 

- data-storage tests, 

- Victim filtering tests, 

- browser annotation safety tests, 

- evaluation dataset validation, 

- metadata validation, 

- collector validation, 

- AI benchmark validation. 

The testing evidence should be interpreted according to the actual test environment available at the time of audit. A test that existed in the repository is not automatically equivalent to a test that was successfully executed during the latest audit. 

## **15.2 Test Strategy** 

The N-ONE testing strategy is designed around the major functional boundaries of the project. 

The overall approach can be represented as: 

N-ONE Testing | ----------------------------------------|           |            |               | v           v            v               v Functional   Boundary     Data/State      AI Evaluation Tests        Tests        Tests             Tests |           |            |               | v           v            v               v 

Authentication  Invalid      CSV/Data       Model Comparison Profiles        Inputs       Unknown DB      Thresholds Victim Search   Face Count   Victim Cache    Dataset Metadata Browser         Paths        Logs             Metrics 

The tests are primarily designed to answer questions such as: 

1. Does the application correctly handle missing configuration? 

2. Are legacy profile names mapped to the correct categories? 

3. Does the unknown-person database count unique identities? 

4. Does clearing unknown data remove the associated stored information? 

5. Can Victim Search be restricted to the selected Victim? 

6. Are all enrolled face-angle files loaded correctly? 

7. Does browser annotation avoid displaying an incorrect identity? 

8. Does the fallback recognition path avoid false identity assignment? 

9. Does the evaluation collector enforce the required face-count rules? 

10. Are dataset paths prevented from escaping the evaluation dataset root? 

11. Are benchmark datasets and metadata represented consistently? 

This makes the test strategy more focused on **observable system behavior** than on internal implementation alone. 

## **15.3 Unit Testing and Behavioral Testing** 

Unit testing is used for relatively isolated pieces of project behavior. 

For example, profile categorization can be tested without running the complete Streamlit interface. 

Similarly, Victim filtering can be tested independently of the complete camera-processing workflow. 

This approach is useful because the N-ONE application contains several operations that can be validated independently: 

Profile Naming ↓ 

Category Detection ↓ Known-Profile Cache ↓ Victim Filtering ↓ Recognition Decision ↓ Result Annotation ↓ 

Logging 

Testing each boundary independently helps identify whether an error originates from: 

- input handling, 

- classification, 

- cache construction, 

- matching, 

- annotation, 

- or persistence. 

## **15.4 Functional Test Cases** 

The following table summarizes the representative functional tests defined for the project. 

|**Te**|**Test Case**|**Expected**|**Evidence**|
|---|---|---|---|
|**st**<br>**ID**||**Result**||
|T0<br>1|Missing<br>authenticat<br>ion secret|System<br>remains<br>unavailable<br>and reports<br>configuration<br>error|load_auth_credentials()|
|T0<br>2|Legacy<br>Member<br>profile|Categorized as<br>Staff|test_profile_labels_support_new_and_l<br>egacy_prefixes|
|T0|Legacy|Categorized as|Same test|
|3|Lost<br>profile|Victim||
|T0|Duplicate|Count uses|test_unknown_count_uses_unique_databa|
|4|unknown<br>DB rows|unique saved<br>IDs|se_ids|
|T0|Clear|Images/|test_clear_unknown_face_data_removes_|
|5|unknown<br>data|cache/CSV<br>tracking reset|photos_and_resets_tracking|
|T0|Victim|Only selected|test_known_face_cache_can_be_limited_|
|6|cache<br>restriction|Victim can<br>match|to_one_victim|
|T0|Five angle|All saved|test_known_face_database_refresh_incl|
|7|files|angles enter<br>cache|udes_all_saved_angles|



|T0|Browser|Green|Browser annotation test|
|---|---|---|---|
|8|unmatched<br>Victim|detection box,<br>no identity||
|T0<br>9|Browser<br>neural<br>selected<br>Victim|Red selected-<br>Victim result|Neural runtime test|
|T1<br>0|Fallback<br>Victim|No false<br>identity label|Fallback test|
|T1<br>1|Dataset<br>path<br>traversal<br>input|Path remains<br>under dataset<br>root|Collector test|
|T1<br>2|Enrollmen<br>t face<br>count|Exactly one<br>face required|Collector tests|
|T1<br>3|Test image<br>face count|At least one<br>face required;<br>multiple<br>allowed|Collector tests|



These tests cover several important project boundaries rather than attempting to simulate the complete application through the browser. 

## **15.5 Authentication Configuration Testing** 

#### **Test ID: T01** 

**Test case:** Missing authentication secret. 

The authentication system depends on credentials supplied through the supported configuration mechanism. 

The test verifies the behavior when the expected authentication configuration is unavailable. 

The expected behavior is not to silently create a default administrator account or continue as an authenticated user. 

Instead, the system should remain unavailable for authenticated operation and report a configuration problem. 

The relevant implementation boundary is: 

_read_secret() 

↓ 

load_auth_credentials() ↓ Validate configuration 

↓ 

Authentication available 

This test is important from both a functional and security perspective because missing authentication configuration should not result in unintended access. 

## **15.6 Legacy Profile Compatibility Testing** 

### **15.6.1 Legacy Member Profile** 

#### **Test ID: T02** 

The project supports current profile terminology while maintaining compatibility with older stored profile naming conventions. 

A legacy profile beginning with: 

Member_ 

is expected to be categorized as: 

##### **Staff** 

The corresponding test verifies that the profile inventory does not incorrectly classify such records as Victims or unknown profiles. 

### **15.6.2 Legacy Lost Profile** 

#### **Test ID: T03** 

The project also supports the older: 

Lost_ 

profile prefix. 

The expected classification is: 

##### **Victim** 

This compatibility behavior is important because existing profile files may have been created using earlier project terminology. 

Therefore, profile categorization testing also functions as a migration/compatibility test. 

## **15.7 Unknown Database Testing** 

### **Test ID: T04 – Duplicate Unknown Records** 

The Unknown Person subsystem maintains information about previously observed unknown individuals. 

A potential data-integrity problem occurs if the underlying CSV contains duplicate rows representing the same unknown ID. 

The test verifies that the displayed unknown-person count is based on **unique saved IDs** rather than simply counting every CSV row. 

For example: 

unknown_001 unknown_001 unknown_002 unknown_003 

should represent: 

Unique Unknown Persons = 3 

rather than: 

CSV Rows = 4 

This distinction is important because multiple sightings can naturally generate multiple records without representing multiple people. 

## **15.8 Unknown Data Clearing Test** 

### **Test ID: T05** 

The project provides functionality for clearing stored unknown-person data. 

The test verifies that clearing the unknown data does not only remove a visual record from the interface. 

The expected behavior includes resetting the relevant: 

- saved unknown photographs, 

- unknown cache, 

- CSV tracking data. 

Conceptually: 

Clear Unknown Data | +---- Remove unknown images | +---- Reset unknown cache | +---- Reset CSV tracking | +---- Refresh application state 

This test is important because incomplete cleanup could cause an old unknown identity to reappear after the operator believes the data has been cleared. 

## **15.9 Victim Target Filtering Test** 

### **Test ID: T06** 

Victim Search is designed as a target-specific operation. 

The operator selects one Victim profile, and the recognition cache used by the search should be restricted to that selected target. 

The expected behavior is: 

Selected Victim | v Target Profile ID | v Filtered Known Cache | v Face Comparison | v Selected Victim / No Match 

The important security and functional property is that another registered Victim or Staff member should not accidentally become the visible result of the selected Victim search. 

This is particularly important because a general known-face search and a target-specific Victim Search have different operational semantics. 

The relevant test is: 

test_known_face_cache_can_be_limited_to_one_victim 

## **15.10 Five-Angle Profile Testing** 

### **Test ID: T07** 

The registration workflow supports multiple face angles for a profile. 

The relevant test verifies that the saved angle files are included when the known-face database is refreshed. 

The intended profile structure can contain multiple views such as: 

Front Left Right Up Down 

These representations can provide more variation during later recognition. 

The test therefore validates the connection between: 

Saved Profile Images ↓ 

Profile Inventory ↓ 

Known Face Database Refresh ↓ 

Recognition Cache 

If an angle is saved successfully but omitted from the recognition cache, the enrollment workflow would appear to work while the actual recognition system would not benefit from that image. 

## **15.11 Browser Annotation Testing** 

Browser-based processing introduces a separate presentation layer. 

The system must distinguish between: 

- detecting a face, 

- determining that the face is not a match, 

- identifying the selected Victim. 

The tests therefore check the visual annotation behavior. 

### **15.11.1 Unmatched Victim Test** 

#### **Test ID: T08** 

When a detected face does not match the selected Victim, the browser annotation should show the detection without assigning an incorrect identity. 

The expected behavior is: 

Face detected ↓ No selected-Victim match ↓ Green detection box ↓ 

No Victim identity label 

The purpose is to prevent the interface from displaying a misleading identity simply because a face was detected. 

## **15.12 Neural Selected-Victim Annotation Test** 

### **Test ID: T09** 

When the neural recognition runtime is available and the selected Victim is correctly matched, the browser annotation should identify the selected Victim using the expected selected-target result styling. 

The expected behavior is represented as: 

Face detected ↓ Neural recognition ↓ Selected Victim matched ↓ 

Red selected-Victim result 

The test therefore validates the relationship between the recognition result and its visual representation. 

## **15.13 Fallback Victim Safety Test** 

### **Test ID: T10** 

N-ONE includes an OpenCV-based fallback path when the required neural recognition runtime is unavailable. 

The fallback path must not create an unsupported identity claim. 

The test therefore verifies that the fallback Victim path does not falsely label a detected face as the selected Victim. 

Conceptually: 

Neural runtime unavailable ↓ OpenCV fallback ↓ Face detection / processing ↓ 

No unsupported identity assignment 

This is an important safety boundary because a lightweight fallback detector should not be treated as equivalent to a neural identity-recognition model. 

## **15.14 Dataset Path Traversal Test** 

### **Test ID: T11** 

The evaluation collector accepts dataset-related file inputs. 

Because filesystem paths can potentially contain traversal sequences, the collector validates that the resulting path remains within the intended dataset root. 

Conceptually: 

User Input Path ↓ Path Resolution ↓ Dataset Root Validation ↓ Allowed? 

/       \ Yes        No |          | Save       Reject 

The expected result is that a malicious or malformed path cannot cause files to be written outside the evaluation dataset directory. 

This test is particularly relevant because the evaluation collector creates files and metadata on the local filesystem. 

## **15.15 Enrollment Face Count Validation** 

### **Test ID: T12** 

The evaluation collector applies a stricter validation rule to enrollment images. 

The expected condition is: 

NumberOfFaces=1NumberOfFaces = 1 

The following conditions should therefore be rejected: 

0 faces 

and: 

2 or more faces 

The reason is that an enrollment image must have an unambiguous identity association. The intended flow is: 

Enrollment Image 

↓ Face Detection ↓ 

Count Faces | +---+---+ |       | 1     0 / >1 |       | Accept    Reject 

This reduces the possibility of accidentally enrolling the wrong person's face. 

## **15.16 Test Image Face Count Validation** 

### **Test ID: T13** 

Test images have a different validation requirement. 

Unlike enrollment, a test image is allowed to contain multiple faces because real surveillance frames may naturally contain more than one person. 

Therefore, the collector requires: 

NumberOfFaces≥1NumberOfFaces \geq 1 

but does not require: 

NumberOfFaces=1NumberOfFaces = 1 

This distinction is important. 

#### **Enrollment** 

Exactly one face 

#### **Testing** 

At least one face 

This reflects the difference between controlled identity enrollment and realistic surveillance testing. 

## **15.17 AI Benchmark Testing** 

In addition to ordinary application tests, N-ONE contains a dedicated evaluation workspace for AI benchmark experiments. 

The benchmark tests are designed to validate: 

- independent enrollment/test paths, 

- model comparisons, 

- threshold decisions, 

- dataset metadata, 

- identity labels, 

- evaluation conditions, 

- metric calculations. 

The evaluation dataset metadata records conditions including: 

- normal, 

- angle, 

- lighting, 

- distance, 

- blur, 

● multiple faces. 

This enables later analysis of whether recognition behavior changes under different visual conditions. 

## **15.18 Independence of Enrollment and Test Data** 

One of the most important properties of the benchmark is the separation between enrollment and test images. 

The system should not evaluate a model using the same image that was used to create the identity representation. 

The conceptual workflow is: 

Enrollment Dataset | v Create Reference | X | X  Same image must not be reused | v Independent Test Dataset | v 

Recognition Evaluation 

This is necessary to reduce the risk of an artificially inflated result caused by testing memorized or identical images. 

## **15.19 Benchmark Metadata Testing** 

The benchmark dataset uses metadata to describe each image. 

The metadata provides information such as: 

- file path, 

- identity, 

- category, 

- split, 

- condition, 

- expected result. 

The expected structure allows an evaluation script to determine whether a particular image belongs to: 

- enrollment, 

- genuine testing, 

- impostor testing, 

- another evaluation category. 

This makes the evaluation reproducible and reduces dependence on manually interpreting filenames. 

## **15.20 Impostor Dataset Evidence** 

The impostor source information records LFW identity/source references and hashes. 

This is useful for traceability because an evaluation result should ideally be connected to the source of the test image. 

Hash values can additionally help establish that a particular file has not silently changed after the benchmark was performed. 

Conceptually: 

Source Image ↓ Dataset File ↓ SHA-256 Hash ↓ Metadata ↓ Benchmark 

This improves reproducibility of the evaluation workspace. 

## **15.21 Testing Boundaries** 

The current testing architecture can be divided into several layers. 

**Testing Layer Main Purpose** 

Unit/behavior testing Validate individual functions and behaviors 

|Boundary testing|Validate invalid or unusual inputs|
|---|---|
|Data testing|Validate CSV/cache/storage behavior|
|Victim safety testing|Prevent incorrect identity assignment|
|Browser annotation testing|Validate visual recognition states|
|Collector testing|Validate evaluation dataset creation|
|Benchmark testing|Compare AI models and thresholds|
|Manual application testing|Validate complete operational workflow|



This layered approach is useful because no single test type can establish the correctness of the complete system. 

## **15.22 Test Gaps** 

The current repository does not provide complete coverage of every operational scenario. 

The following gaps remain explicitly identified. 

### **15.22.1 Full Streamlit Browser End-to-End Testing** 

A complete automated browser test covering: 

Login 

- → Profile Registration 

- → Camera 

- → Victim Search 

- → Result 

- → Logging 

- → Logout 

is not currently available. 

The existing browser-related tests focus on annotation and processing behavior rather than complete user-interface automation. 

### **15.22.2 Multi-User Concurrency Testing** 

The project does not contain a dedicated concurrency benchmark involving multiple simultaneous users or operators. 

This is relevant because the current application uses local files and CSV-based persistence. 

Potential future testing should examine: 

- simultaneous writes, 

- simultaneous profile changes, 

- simultaneous logging, 

- concurrent camera sessions. 

### **15.22.3 Staff Benchmark** 

A dedicated quantitative Staff recognition benchmark is not currently available. 

Therefore, no numerical Staff accuracy should be claimed from the existing test suite. 

### **15.22.4 Unknown Re-ID Benchmark** 

Unknown-person continuity is implemented, but a formal labeled benchmark measuring Re-ID performance is not currently available. 

### **15.22.5 Threat Detection Benchmark** 

The threat detection module requires an independent labeled dataset to measure its classification performance. 

The current face-recognition benchmark does not provide this evidence. 

### **15.22.6 Labeled Video Sequence Testing** 

The current benchmark does not contain the labeled video sequences required to evaluate: 

- 1-frame recognition, 

- 3-frame confirmation, 

- 5-frame confirmation, 

- temporal consistency, 

- confirmation latency. 

Therefore, multi-frame performance remains unmeasured. 

## **15.23 Current Validation Status** 

The final audit attempted to execute the available test suite using the project Python environments. 

However, the checked-in new_venv environment does not contain the pytest package. 

The system Python 3.14 environment also reports: 

No module named pytest 

Therefore, a fresh successful test-run result cannot be claimed from this audit. 

This distinction is important: 

The existence of test files in the repository is not equivalent to successfully executing those tests during the final audit. 

The current validation status should therefore be documented separately from historical test evidence. 

## **15.24 Historical Test Evidence** 

A previous repository audit recorded: 

24 passed 1 failed 1 error 

However, this result is **historical evidence** . 

It should not be represented as the result of the latest audit because the current audit did not successfully reproduce the complete test run. 

The historical failure concerned the expected ordering of columns in: 

evaluation/dataset_metadata.csv 

The test expected: 

file_path 

to appear first, while the checked-in collector schema writes: 

id 

as the first column. 

Therefore, there is a schema-order inconsistency between the test expectation and the checked-in collector output. 

## **15.25 Metadata Column-Order Issue** 

The identified issue can be represented as: 

Test Expectation 

| v file_path first | X | v Checked-in Collector | v 

id first 

The problem concerns the expected order of metadata columns rather than necessarily indicating that the data itself is semantically incorrect. 

However, because automated tests should agree with the current schema, the discrepancy should be resolved before final submission or explicitly documented as a known test issue. 

A final report should not silently claim that all tests pass while this inconsistency remains unresolved. 

## **15.26 Temporary-Directory Error** 

The historical audit also recorded an error related to temporary-directory handling. 

The available evidence identifies this as an **environment-related error** rather than a demonstrated functional failure of the N-ONE application. 

Nevertheless, because the current audit could not reproduce the complete test suite, the issue should remain visible in the testing documentation until it can be reproduced and resolved. 

This follows the principle: 

An unresolved test error should be documented rather than silently removed from the project record. 

## **15.27 Evaluation Documentation Contradiction** 

Another validation issue exists within the evaluation documentation. 

The evaluation workspace contains actual: 

- populated dataset information, 

- measured CSV result files, 

- benchmark evidence. 

However, older versions of: 

evaluation/README.md 

and: 

evaluation/dataset/README.md 

still describe the evaluation workspace as having no real evaluation data. 

Therefore, the current repository contains a documentation-state contradiction. 

Conceptually: 

Older README 

"No real evaluation data" 

| X | Current Workspace Populated dataset + measured CSVs 

The measured CSV files contain explicit benchmark values and are therefore used as evidence in Chapter 14. 

The older README statements are treated as **legacy documentation** , not as current benchmark results. 

## **15.28 Importance of Documentation Consistency** 

Documentation consistency is important in a research-oriented project because a reviewer may inspect both the source code and the supporting documentation. 

If the README says: 

No evaluation data exists 

while the repository simultaneously contains populated benchmark results, the reviewer may be uncertain about which information represents the current project state. 

Therefore, the final submission should clearly distinguish: 

- current evaluation status, 

- historical documentation, 

- measured results, 

● future evaluation plans. 

A simple status table can help: 

**Component Current Status** Evaluation workspace Populated Benchmark result CSVs Present Victim benchmark Measured Staff benchmark Not measured Unknown Re-ID benchmark Not measured Threat benchmark Not measured Multi-frame benchmark Not available Older README status Legacy/inconsistent 

## **15.29 Testing Evidence Classification** 

For the final project report, testing evidence should be classified into three categories. 

#### **A. Current reproducible evidence** 

Evidence that can be successfully reproduced in the current environment. 

#### **B. Historical evidence** 

Results obtained during a previous audit or test execution. 

#### **C. Planned/unavailable evidence** 

Tests that are defined or desirable but have not been successfully executed. 

This classification prevents historical results from being incorrectly presented as current results. 

## **15.30 Recommended Final Testing Workflow** 

Before final submission, the testing process should ideally follow: 

1. Prepare clean test environment 

- ↓ 

2. Install required dependencies ↓ 

3. Verify pytest availability 

- ↓ 

4. Run complete automated suite 

- ↓ 

5. Capture terminal output 

- ↓ 

6. Investigate failures/errors 

- ↓ 

7. Re-run after corrections 

- ↓ 

8. Validate evaluation metadata 

↓ 

9. Validate benchmark CSVs ↓ 

10. Run manual application checks 

- ↓ 

11. Capture screenshots 

- ↓ 

12. Record final evidence 

The final report should only state **“all tests passed”** if the complete suite has actually been executed successfully in the documented environment. 

## **15.31 Testing Traceability** 

A useful testing traceability structure for N-ONE is: 

|**Requirement / Feature**|**Test Evidence**|
|---|---|
|Authentication|T01|
|Legacy Staff classification|T02|
|Legacy Victim classification|T03|



|Unknown identity counting|T04|
|---|---|
|Unknown data reset|T05|
|Victim target restriction|T06|
|Multi-angle profile loading|T07|
|Browser unmatched state|T08|
|Neural Victim result|T09|
|Fallback safety|T10|
|Dataset path security|T11|
|Enrollment validation|T12|
|Test-image validation|T13|
|AI model comparison|Benchmark scripts|
|Threshold evaluation|Benchmark scripts|
|Multi-frame evaluation|Not available|
|Staff benchmark|Not available|
|Unknown benchmark|Not available|
|Threat benchmark|Not available|



This table provides a direct relationship between the project's functionality and the available validation evidence. 

## **15.32 Testing Limitations** 

The testing system itself has limitations. 

First, most automated tests are behavior-oriented rather than complete end-to-end tests. 

Second, the absence of a successful current pytest run means that the latest audit cannot claim a complete automated pass status. 

Third, the AI benchmark and application tests operate at different levels. A successful model benchmark does not prove that the complete Streamlit application behaves correctly. 

Similarly, successful unit tests do not establish real-world face-recognition accuracy. 

The following distinction is therefore important: 

Unit Test ≠! Application End-to-End Test ≠! AI Benchmark ≠! Real-World Deployment Validation 

Each provides different evidence. 

## **15.33 Overall Testing Assessment** 

The N-ONE project contains a meaningful testing foundation covering several critical behaviors. 

The strongest areas of the current test design include: 

- authentication configuration handling, 

- profile categorization, 

- unknown-person data integrity, 

- Victim target filtering, 

- multi-angle cache loading, 

- browser annotation safety, 

- fallback identity safety, 

- evaluation path validation, 

- enrollment face-count validation, 

- test-image validation, 

- AI benchmark and threshold evaluation. 

At the same time, the current testing evidence has clearly documented limitations. 

The most important outstanding areas are: 

- complete reproducible pytest execution, 

- full Streamlit browser end-to-end testing, 

- concurrency testing, 

- independent Staff benchmark, 

- Unknown Re-ID benchmark, 

- Threat Detection benchmark, 

- labeled multi-frame video evaluation, 

- resolution of the metadata column-order mismatch, 

● cleanup/update of contradictory legacy evaluation README files. 

## **15.34 Chapter Summary** 

Software testing in N-ONE is designed around the project's major functional and AI-processing boundaries. The existing tests verify important behaviors such as authentication configuration, profile classification, unknown-person data handling, Victim target restriction, browser annotation, fallback safety, and evaluation dataset validation. 

The AI evaluation layer separately validates model comparison and threshold behavior using independent enrollment and test data. This separation is important because software correctness and recognition-model performance represent different dimensions of system validation. 

The current audit, however, does **not** provide evidence for claiming that the complete automated test suite currently passes. The checked-in environments do not contain pytest, and therefore the historical result of 24 passed, 1 failed, and 1 error must remain classified as historical evidence. The metadata column-order discrepancy and temporary-directory issue must also remain documented until they are reproduced and resolved. 

Similarly, the absence of Staff, Unknown Re-ID, Threat Detection, multi-user concurrency, full browser end-to-end, and labeled multi-frame tests must remain visible rather than being represented as completed validation. 

Overall, the testing structure provides a strong foundation for demonstrating functional correctness and AI evaluation methodology, while the identified gaps define the next stage of validation required for a more comprehensive project submission. 

**For the final report, Chapter 15 should ideally be accompanied by a testing evidence figure showing the test architecture, test-case flow, and current validation status.** 

## **CHAPTER 16 – SECURITY, PRIVACY, AND ETHICAL CONSIDERATIONS** 

### **16.1 Introduction** 

Security, privacy, and ethical considerations are particularly important in N-ONE because the system processes **facial images, identity-related information, camera locations, unknownperson records, and event histories** . 

Unlike a conventional image-processing application, N-ONE can associate a detected face with a registered profile such as a Staff member or Victim. Consequently, incorrect access control, inappropriate data handling, or incorrect interpretation of recognition results can have consequences beyond a normal software error. 

The security design of N-ONE therefore focuses on several areas: 

- authentication, 

- role-based authorization, 

- failed-login handling, 

- protection of application secrets, 

- controlled administrative operations, 

- local data handling, 

- privacy, 

- human review, 

- responsible interpretation of AI results, 

- dataset licensing and attribution. 

The current implementation provides several protective mechanisms, but it does **not** implement all controls that would normally be expected in a production-grade identity or surveillance platform. 

## **16.2 Authentication and Authorization** 

Authentication is the first security boundary of N-ONE. 

The application does not intentionally provide unrestricted access to the main operational interface when valid authentication credentials are unavailable. 

The basic security flow can be represented as: 

User | v Enter Credentials | v Credential Configuration | v Credential Comparison | +------------------+ |                  | Valid             Invalid |                  | v                  v Authenticated     Failure Count |                  | v                  v Role Assigned     Lockout Check |                  | v                  v 

Admin / Operator  Temporary Lock 

This provides an initial access-control boundary before users can access the system's operational features. 

## **16.3 Fail-Closed Authentication** 

The system is designed to fail closed when the required authentication configuration is missing. 

This means that missing credentials should not result in: 

- automatic administrator access, 

- an anonymous privileged session, 

- silently generated credentials. 

Instead, the application reports a configuration problem and prevents normal authenticated operation. 

This is important because a missing secret should be treated as a configuration/security problem rather than as permission to continue without authentication. 

## **16.4 Credential Comparison** 

The authentication implementation uses: 

hmac.compare_digest 

for secret comparison. 

The purpose of using a constant-time comparison primitive is to avoid relying on an ordinary string comparison for sensitive secret values. 

The relevant security principle is: 

Credential Input 

| 

v 

Secure Comparison 

| 

v 

Authentication Decision 

This does not mean that the entire authentication system is equivalent to a complete enterprise identity-management solution. It represents a specific protective measure within the application's local authentication mechanism. 

## **16.5 Failed Login Handling** 

N-ONE includes session-level protection against repeated failed authentication attempts. 

The configured behavior is: 

Maximum Failed Attempts = 5 Lockout Period = 60 seconds 

The conceptual workflow is: 

Login Attempt | v Credentials Valid? /          \ Yes           No |              | v              v Login       Increment Failure Count | v Attempts >= 5? /       \ No         Yes |           | v           v 

Allow retry   60-sec lockout 

This provides basic protection against repeated password guessing within the current application session. 

The control should not be interpreted as a complete enterprise-grade brute-force prevention system because the repository does not establish the presence of centralized identity monitoring, distributed rate limiting, or persistent authentication auditing. 

## **16.6 Role-Based Authorization** 

N-ONE separates authenticated users into operational roles. 

The two principal roles are: 

- **Administrator** 

- **Operator** 

The purpose of this separation is to prevent every authenticated user from automatically receiving administrative capabilities. 

The conceptual access structure is: 

Authenticated User 

| +------+------+ |             | v             v Administrator   Operator |             | v             v Administrative       Monitoring Controls          Operations 

## **16.7 Administrator Privileges** 

Administrator-only operations include functionality such as: 

- Staff registration, 

- Victim registration, 

- model configuration, 

- clearing registered profiles, 

- resetting audit-related data, 

- destructive local-data operations. 

These functions can directly modify system state or remove stored information. 

Restricting them to the Administrator role reduces the possibility of an ordinary operator unintentionally changing system configuration or deleting evidence. 

## **16.8 Operator Privileges** 

The Operator role is designed primarily for monitoring and review. 

Operators can use the operational portions of the application, including activities such as: 

- monitoring camera feeds, 

- running searches, 

- reviewing inventory, 

- reviewing logs, 

- using available recognition workflows. 

The interface does not expose Administrator-only controls to the Operator role. 

This establishes a basic principle of **least privilege at the application UI level** . 

However, because the project uses local files for persistence, UI-level authorization should not be interpreted as equivalent to operating-system-level access control over those files. 

## **16.9 Password Security Limitations** 

Although N-ONE includes authentication and failed-login handling, the current repository does not demonstrate a complete enterprise password-management architecture. 

The implementation does **not** establish the presence of: 

- password hashing, 

- password rotation, 

- multi-factor authentication, 

- external identity federation, 

- centralized identity management, 

- persistent login audit storage. 

Therefore, the authentication mechanism should be understood as a project-level application authentication layer rather than a complete enterprise identity platform. 

## **16.10 Secret Management** 

Authentication credentials are expected to be supplied through environment variables or Streamlit Secrets rather than being committed directly into source code. 

The intended principle is: 

Source Code 

| X | Credentials | 

+---- Environment Variables | 

+---- Streamlit Secrets 

This separation reduces the risk of accidentally placing credentials directly in the project repository. 

However, the use of environment variables or application secrets does not automatically guarantee secure deployment. 

The deployment operator remains responsible for: 

- protecting the host system, 

- protecting environment variables, 

- restricting secret access, 

- preventing accidental repository commits, 

- securing deployment configuration. 

## **16.11 Missing Password Hardening Controls** 

A production deployment would normally require additional password-security controls. 

The current repository does not establish: 

#### **Password Hashing** 

There is no demonstrated password-hashing system in the documented implementation. 

#### **Password Rotation** 

The system does not demonstrate a forced password-expiration or rotation mechanism. 

#### **Multi-Factor Authentication** 

MFA is not implemented in the current project evidence. 

#### **External Identity Federation** 

There is no demonstrated integration with an external identity provider. 

#### **Persistent Login Audit** 

The project does not establish a dedicated persistent authentication audit database. 

These are therefore documented as security limitations rather than being presented as implemented features. 

## **16.12 Data Protection** 

N-ONE processes several categories of potentially sensitive information. 

These include: 

- Staff photographs, 

- Victim photographs, 

- unknown-person photographs, 

- camera locations, 

- timestamps, 

- recognition-related event records, 

- Victim sighting histories, 

- unknown-person sighting histories, 

- audit records. 

The data flow can be represented as: 

Camera / Registration | v 

Face/Image Processing 

| +----------------+ |                | v                v Registered Data     Unknown Data |                | +-------+--------+ | v CSV / Image Files | v Dashboard / Review 

## **16.13 Local File Storage** 

The current project stores important data locally using ordinary image files and CSV-based records. 

This includes information such as: 

- face crops, 

- registered profile photographs, 

- unknown-person images, 

- sighting information, 

- event histories. 

This architecture is appropriate for the project's current local/small-scale implementation but introduces additional security considerations. 

For example, access to the application UI does not necessarily prevent an operating-system user with filesystem access from directly opening the underlying files. 

Therefore: 

Application-level authorization and filesystem-level authorization are separate security boundaries. 

## **16.14 Encryption at Rest** 

The current source does not implement encryption at rest for stored: 

- face images, 

- unknown images, 

- CSV records, 

- location histories. 

Therefore, if the project were deployed in an environment where stored facial information requires stronger protection, additional storage-security mechanisms would be necessary. 

Potential future controls could include encrypted storage and appropriately restricted filesystem permissions, but these should not be described as currently implemented N-ONE features. 

## **16.15 File-Level Access Control** 

The current project does not establish a dedicated file-permission management layer. 

Consequently, protection of the stored data depends partly on the security of the operating system and deployment environment. 

A production deployment should consider: 

- restricting application-directory permissions, 

- separating application and data directories, 

- limiting direct access to face-image folders, 

- restricting access to CSV logs, 

- securing backup locations. 

These are deployment-level security responsibilities rather than demonstrated features of the current application. 

## **16.16 Data Retention** 

The current implementation does not establish a formal automatic data-retention policy. 

There is no demonstrated mechanism that automatically deletes: 

- old face images, 

- old unknown-person records, 

- old sighting events, 

- old camera-location records. 

This creates an important privacy consideration. 

Long-term storage of facial and location information may increase privacy exposure if the data is retained longer than operationally necessary. 

A future production deployment should define: 

Data Created | v Retention Period | v 

Review / Expiration | 

v 

Secure Deletion 

The actual retention period should be determined according to the deployment's legitimate purpose and applicable requirements. 

## **16.17 Data Deletion** 

N-ONE provides administrative controls for destructive local-data operations. 

However, the current source does not demonstrate a formal deletion-approval workflow. 

Therefore, deletion should not be represented as equivalent to a regulated records-management system. 

A stronger production implementation could introduce: 

- deletion authorization, 

- deletion audit records, 

- confirmation workflow, 

- retention-policy enforcement, 

- secure deletion procedures. 

## **16.18 Privacy Considerations** 

Face recognition involves biometric information and therefore requires particular care in system design and operation. 

N-ONE should only be used in circumstances where the operator has an appropriate basis and authority to collect and process the relevant information. 

Depending on the deployment context, appropriate considerations may include: 

- authorization, 

- notice, 

- consent where applicable, 

- lawful basis, 

- purpose limitation, 

- data minimization, 

- retention limits, 

- controlled access, 

- human review. 

The project itself does not establish legal compliance with a particular jurisdiction. 

Therefore, the application should not be presented as automatically compliant with any specific privacy or data-protection law. 

## **16.19 Data Minimization** 

The system should collect and retain only information necessary for its intended operational purpose. 

For example, if an evaluation only requires a face image and an identity label, unrelated personal information should not be added to the evaluation dataset. 

Similarly, camera-location information should only be retained when it is required for the intended monitoring workflow. 

A conceptual privacy-aware workflow is: 

Collect Data 

| v Purpose Check | v Necessary? /    \ Yes     No |       | v       v Store   Do Not Collect 

This reduces unnecessary exposure of personal information. 

## **16.20 Ethical Use of Face Recognition** 

Technical functionality does not automatically establish that a system should be used in every possible situation. 

N-ONE's face-recognition capability should therefore be operated with appropriate human oversight. 

A recognition result should be treated as an **AI-generated indication requiring contextual interpretation** , rather than an unquestionable fact. 

The system should not be used as the sole basis for: 

- detention, 

- disciplinary action, 

- emergency escalation, 

- accusations, 

- legal conclusions. 

This is especially important because face recognition can produce both false positives and false negatives. 

## **16.21 Match Distance Is Not a Percentage Certainty** 

The recognition system uses a distance metric and a threshold. 

For example: 

d≤τd \leq \tau 

indicates that the candidate satisfies the configured matching rule. 

However, this does **not** mean: 

Distance = X ↓ Confidence = X% 

A raw cosine distance should not automatically be converted into a percentage certainty. 

Therefore, the report should avoid statements such as: 

“The system is 95% sure that this is the Victim” 

unless a separately validated calibration methodology actually establishes such a probability interpretation. 

The current benchmark provides distance-based decision results and classification metrics, not calibrated identity probabilities. 

## **16.22 False Positive and False Negative Risks** 

Two important error types must be considered. 

#### **False Positive** 

An individual is incorrectly identified as the selected Victim. 

Other Person 

↓ 

Incorrect Victim Match 

↓ 

False Positive 

#### **False Negative** 

The actual Victim is present but the system fails to identify them. 

Actual Victim 

↓ No Match ↓ 

False Negative 

The benchmark in Chapter 14 demonstrates that these errors are measurable and that threshold selection affects their behavior. 

Therefore, neither a successful match nor a non-match should automatically be treated as infallible evidence. 

## **16.23 Unknown Person Identity** 

N-ONE can assign identifiers such as: 

unknown_001 unknown_002 unknown_003 

These identifiers represent **locally maintained system identities** , not confirmed real-world identities. 

For example: 

unknown_003 

means that the system has associated several observations with its internal Unknown Person record. 

It does **not** establish: 

- the person's legal name, 

- their verified identity, 

- their criminal status, 

- their intent. 

This distinction is essential for responsible use. 

## **16.24 Unknown Re-Identification and Privacy** 

Unknown-person re-identification introduces an additional privacy consideration. 

The system may determine that two observations appear to belong to the same locally maintained unknown identity. 

Conceptually: 

Observation 1 | v unknown_003 ^ | Observation 2 

This establishes continuity within the system's own representation. 

It should not automatically be interpreted as verified real-world identity. 

The operator should therefore treat the unknown ID as an internal tracking identifier. 

## **16.25 Threat Detection Interpretation** 

The threat-detection subsystem uses heuristic/contour-based processing. 

The system may produce an output such as: 

##### **Possible weapon** 

or: 

##### **Possible threat/fire** 

The wording is intentionally qualified. 

A contour-based detection result cannot by itself prove that a physical object is a weapon or that an event is actually a threat. 

Therefore: 

Possible Threat ≠! Confirmed Threat 

and: Possible Weapon ≠! 

Verified Weapon 

This distinction should be maintained in both the application interface and the project report. 

## **16.26 Human-in-the-Loop Principle** 

N-ONE should be operated with human review for important decisions. 

A suitable conceptual workflow is: 

Camera Input | v AI Processing | v Candidate Result | v Human Review | +--------+ |        | v        v Confirm   Reject / Investigate 

The AI system provides an observation or candidate result, while the human operator evaluates the broader context. 

This approach reduces the risk of treating an automated output as an unquestionable conclusion. 

## **16.27 Privacy and Security Threat Model** 

The major security/privacy risks relevant to N-ONE can be summarized as follows. 

|**Threat**|**Potential Impact**|**Relevant Control /**<br>**Limitation**|
|---|---|---|
|Unauthorized login|Access to monitoring<br>functions|Authentication|
|Repeated login attempts|Credential guessing|Session lockout|



|Credential exposure|Account compromise|Environment/Secrets<br>recommended|
|---|---|---|
|Unauthorized profile<br>modification|Incorrect recognition data|Admin-only controls|
|Direct filesystem access|Exposure of face data|OS/deployment responsibility|
|Stored face-image<br>exposure|Privacy impact|No encryption at rest currently|
|Excessive data retention|Long-term privacy exposure|Formal retention not<br>implemented|
|Incorrect Victim match|Incorrect identity association|Target restriction + threshold<br>testing|
|False negative|Missed Victim|Benchmarking and threshold<br>analysis|
|Unknown ID misuse|Incorrect real-world<br>interpretation|Internal ID only|
|Threat false positive|Incorrect escalation|Human review / qualified<br>wording|
|Dataset misuse|Licensing/compliance issue|Source/terms documentation|



## **16.28 Security Control Summary** 

The current security controls can be divided into implemented and missing controls. 

|**Security Area**|**Current Status**|
|---|---|
|Authentication|Implemented|
|Fail-closed missing credentials|Implemented|
|Secure secret comparison|Implemented|
|Session failed-attempt lockout|Implemented|



|Admin/Operator separation|Implemented|
|---|---|
|Admin-only destructive controls|Implemented|
|Environment/Secrets credential support|Implemented|
|Password hashing|Not demonstrated|
|Password rotation|Not implemented|
|MFA|Not implemented|
|External identity federation|Not implemented|
|Encryption at rest|Not implemented|
|Formal retention policy|Not implemented|
|File-level access-control layer|Not implemented|
|Persistent login audit store|Not demonstrated|
|Human review principle|Operational requirement|
|Threat-result qualification|Implemented in terminology|



This table prevents security features from being overstated. 

## **16.29 Dataset Licensing and Attribution** 

The AI evaluation process uses an impostor source file that identifies **LFW (Labeled Faces in the Wild)** as the source and preserves source references and a terms note. 

This is important because datasets obtained from external sources may have conditions governing: 

- research use, 

- redistribution, 

- attribution, 

- publication, 

- derivative use. 

The existence of a source reference in the repository improves traceability, but it does not by itself establish legal compliance with every possible use. 

Before publishing the project, the dataset's applicable terms should therefore be reviewed again. 

The final report should retain appropriate dataset attribution according to the applicable source terms. 

## **16.30 Research Reproducibility and Dataset Ethics** 

Dataset documentation is also part of ethical research practice. 

The project should make it possible to determine: 

- where evaluation data came from, 

- which data was used for enrollment, 

- which data was used for testing, 

- which images represented impostors, 

- what conditions were tested, 

- which metrics were calculated. 

At the same time, personally identifiable or biometric data should not be unnecessarily published. 

Therefore, reproducibility and privacy must be considered together. 

## **16.31 Ethical Limitations of the Evaluation** 

The benchmark results described in Chapter 14 should not be generalized beyond the tested population and conditions. 

A small benchmark cannot establish that the recognition system will behave identically across: 

- all demographic groups, 

- all camera systems, 

- all environmental conditions, 

- all image qualities, 

- all operational settings. 

The current project also does not provide a dedicated fairness or demographic-bias evaluation. 

Therefore, no claim about demographic fairness should be made from the current benchmark. 

A future research study would need a properly designed and ethically sourced dataset to investigate such questions. 

## **16.32 Responsible Interpretation of AI Results** 

The following interpretation rules should be maintained throughout the N-ONE system: 

|**System Output**|**Correct Interpretation**|
|---|---|
|Victim match|Candidate match according to configured recognition criteria|
|Match distance|Model-specific similarity/distance measurement|
|Unknown ID|Local system tracking identifier|
|Possible weapon|Heuristic indication requiring review|
|Possible threat/fire|Heuristic indication requiring review|
|No match|Recognition system did not satisfy its configured threshold|
|False negative|Genuine target was present but not accepted in the benchmark|
|False positive|Impostor was incorrectly accepted in the benchmark|



This terminology prevents technical outputs from being transformed into stronger claims than the system evidence supports. 

## **16.33 Production Security Recommendations** 

If N-ONE were extended beyond a local academic deployment, additional controls would be appropriate. 

Potential improvements include: 

#### **Authentication** 

- password hashing, 

- MFA, 

- centralized identity provider, 

- password rotation, 

- persistent authentication auditing. 

#### **Data Protection** 

- encryption at rest, 

- encrypted backups, 

- restricted filesystem permissions, 

- controlled data access. 

#### **Privacy** 

- documented retention periods, 

- automated expiry, 

- deletion workflows, 

- data minimization, 

- privacy notices where appropriate. 

#### **Application Security** 

- database-backed transactions, 

- secure session management, 

- centralized logging, 

- role enforcement at the backend/data layer, 

- stronger concurrent-access controls. 

These are **future security improvements** , not current implemented capabilities. 

## **16.34 Security and Privacy Architecture** 

The overall security/privacy boundary of N-ONE can be represented as: 



<!-- Start of picture text -->
                   N-ONE<br>                      |<br>        +-------------+-------------+<br>        |                           |<br>        v                           v<br>   Access Control              Data Processing<br>        |                           |<br>   Authentication              Face Images<br>   Role Separation             Unknown Data<br>   Login Lockout               Locations<br>        |                       Event Logs<br>        |                           |<br>        +-------------+-------------+<br>                      |<br>                      v<br>                Human Review<br>                      |<br>                      v<br>              Operational Decision<br><!-- End of picture text -->

The architecture demonstrates that security is not limited to login functionality. Data handling and interpretation of AI outputs are equally important. 

## **16.35 Overall Security and Ethical Assessment** 

N-ONE provides a basic security foundation through: 

- authentication, 

- fail-closed behavior, 

- secure credential comparison, 

- failed-login lockout, 

- Administrator/Operator separation, 

- restricted administrative controls, 

- controlled Victim target filtering. 

At the same time, the project currently does not implement several controls expected in a production-grade biometric surveillance platform, particularly: 

- password hashing, 

- MFA, 

- encryption at rest, 

- formal retention management, 

- dedicated file-level access control, 

- persistent identity-management infrastructure. 

The privacy model therefore depends partly on the security of the deployment environment and the operational discipline of system administrators. 

From an ethical perspective, N-ONE outputs should be treated as **decision-support information rather than unquestionable conclusions** . A recognition match is not a probability guarantee, an unknown identifier is not a verified real-world identity, and a possible threat is not proof of a weapon or malicious activity. 

The system should therefore remain subject to appropriate human review and authorized use. 

## **16.36 Chapter Conclusion** 

Security, privacy, and ethical considerations form an important part of the N-ONE design because the system handles facial images, identity-related records, unknown-person histories, camera locations, and recognition events. 

The implemented authentication and authorization controls provide a basic security boundary, including fail-closed behavior, secure secret comparison, session lockout, and separation between Administrator and Operator functionality. 

However, the current implementation should not be represented as a complete production-grade security or biometric privacy solution. Important controls such as password hashing, MFA, encryption at rest, formal retention management, and persistent identity auditing are not demonstrated in the repository. 

The ethical design principle of N-ONE is therefore based on **controlled use, qualified AI outputs, and human review** . Recognition results should be interpreted within the limitations of the model and evaluation dataset. Similarly, unknown-person identifiers and heuristic threat alerts must not be converted into unsupported real-world conclusions. 

Finally, external evaluation datasets such as LFW must be used and attributed according to their applicable terms. The presence of source references in the project improves traceability, but final publication and deployment responsibilities remain separate from the technical implementation itself. 

Overall, N-ONE demonstrates a security-aware and privacy-conscious project architecture while clearly identifying the controls that would need to be strengthened before deployment in a higherrisk or production environment. 

## **CHAPTER 17 – LIMITATIONS AND FUTURE SCOPE** 

### **17.1 Introduction** 

Every software and AI-based system has practical limitations, and identifying these limitations is an important part of a technical project evaluation. The purpose of this chapter is not to indicate that N- ONE is incomplete, but to clearly define the boundaries within which the current implementation and evaluation can be interpreted. 

N-ONE combines face recognition, Victim Search, Staff recognition, Unknown Person Re-ID, threat detection, camera processing, local data storage, and a Streamlit-based interface. These components have different technical requirements and therefore cannot all be evaluated using the same dataset or metric. 

The current evaluation provides measurable evidence for the **Victim Face Recognition** subsystem, while several other components remain implemented but not quantitatively benchmarked. 

Therefore, this chapter separates: 

- limitations established by the current implementation, 

- limitations of the evaluation, 

- operational limitations, 

- security limitations, 

- scalability limitations, 

- and future development opportunities. 

## **17.2 Current Limitations** 

### **17.2.1 Small Evaluation Dataset** 

The current AI benchmark uses a relatively small dataset compared with a real-world surveillance deployment. 

The Victim benchmark contains a limited number of: 

- Victim identities, 

- enrollment images, 

- genuine test images, 

- impostor identities, 

- impostor images. 

As a result, the benchmark provides useful experimental evidence but cannot establish universal recognition performance. 

A larger evaluation would be required to determine how the system behaves across a wider range of people and environmental conditions. 

The current result should therefore be interpreted as: 

Performance under the evaluated dataset and experimental protocol. 

It should not be interpreted as: 

Guaranteed performance for every deployment environment. 

## **17.2.2 Still-Image-Oriented Benchmark** 

The current face-recognition benchmark primarily evaluates still images. 

This is different from a continuous surveillance environment in which the system may process a sequence of frames. 

A real camera stream can contain: 

- motion blur, 

- temporary occlusion, 

- changing illumination, 

- face detector instability, 

- changing head pose, 

- partial face visibility, 

- multiple simultaneous faces. 

The current benchmark does not provide sufficient labeled video sequences to quantitatively evaluate these conditions over time. 

Therefore, the benchmark cannot establish the performance of N-ONE as a complete long-duration video surveillance system. 

## **17.2.3 Staff Recognition Accuracy Not Measured** 

Staff recognition is implemented as part of the N-ONE recognition workflow. 

However: 

**Staff-specific recognition accuracy is Not measured in the current implementation/evaluation.** 

This distinction is important. 

The existence of Staff recognition functionality does not automatically provide a numerical Staff recognition accuracy. 

A dedicated Staff evaluation would require: 

- Staff enrollment images, 

- independent Staff test images, 

- non-Staff impostors, 

- controlled test conditions, 

- threshold analysis, 

- TP/TN/FP/FN measurements. 

Until such a benchmark is completed, the report should not assign an accuracy percentage to Staff recognition. 

## **17.2.4 Unknown Re-ID Accuracy Not Measured** 

N-ONE implements Unknown Person Re-ID functionality. 

The system can create local unknown identifiers and associate later observations with previously stored unknown records. 

However: 

##### **Unknown Re-ID accuracy is Not measured in the current implementation/evaluation.** 

This is a separate evaluation problem from Victim face recognition. 

A dedicated Re-ID benchmark would need to determine whether observations belonging to the same unknown person are correctly grouped while different people remain separated. 

The absence of this benchmark means that the current implementation should be described as a **functional Unknown Re-ID mechanism** , rather than as a quantitatively validated Re-ID system. 

## **17.2.5 Threat Detection Accuracy Not Measured** 

The Threat Detection module uses heuristic image-processing techniques. 

The current project does not provide a dedicated labeled threat dataset sufficient to calculate formal classification metrics. 

Therefore: 

##### **Threat-detection accuracy is Not measured in the current implementation/evaluation.** 

Metrics such as: 

PrecisionPrecision RecallRecall F1F1 FARFAR 

and 

FRRFRR 

should not be assigned to the threat subsystem without an appropriate labeled evaluation. 

The existing threat output should therefore remain qualified as a **possible threat/possible weapon indication** requiring human review. 

## **17.2.6 Multi-Frame Metrics Unavailable** 

The current evaluation does not contain sufficient labeled video sequences to measure: 

- one-frame performance, 

- three-frame confirmation, 

- five-frame confirmation, 

- confirmation latency, 

- temporal consistency, 

- false alerts across sequences. 

Therefore, multi-frame metrics remain: 

##### **Not Available** 

No claim is made that multi-frame confirmation improves recognition performance until this is experimentally tested. 

## **17.2.7 OpenCV Fallback Limitation** 

N-ONE provides an OpenCV-based fallback when the neural recognition runtime is unavailable. 

This fallback is useful for maintaining portions of the application's computer-vision workflow under constrained environments. 

However, the active fallback is **not a trained neural identity model** . 

Therefore, the fallback should not be represented as equivalent to: 

- FaceNet, 

- FaceNet512, 

- ArcFace, 

- or another neural face-recognition embedding model. 

This creates an important architectural boundary: 

Neural Runtime Available 

| v Neural Face Representation | v Identity Matching 

Neural Runtime Unavailable | v OpenCV Fallback | v Limited Face Processing | v No Unsupported Identity Claim 

This separation helps prevent the fallback mechanism from being interpreted as having the same identity-recognition capability as the evaluated neural models. 

## **17.2.8 Environmental Conditions** 

Face recognition performance can be affected by image and environmental conditions. 

The current project identifies several challenging conditions, including: 

- lighting variation, 

- pose variation, 

- blur, 

- camera distance, 

- occlusion, 

- face detector errors, 

- multiple faces. 

For example, poor illumination may reduce the quality of the face region available for recognition. 

Similarly, a partially visible face may produce a representation that differs substantially from the enrollment representation. 

A small or distant face can also reduce the amount of usable facial information. 

Therefore, benchmark results obtained under a particular dataset should not automatically be generalized to all environmental conditions. 

## **17.2.9 Multiple-Face Limitation** 

Profile enrollment requires an unambiguous face. 

Therefore, enrollment validation requires exactly one detected face. 

Real surveillance frames, however, may contain: 

Person A     Person B     Person C ↓            ↓            ↓ 

Face 1       Face 2       Face 3 

This introduces additional complexity during recognition because the system must determine which detected face corresponds to which identity or whether any detected face matches the selected target. 

The current Victim Search workflow is target restricted, but multi-person surveillance remains an important evaluation area for future work. 

## **17.2.10 WebRTC Processing Difference** 

N-ONE supports browser-based video processing through WebRTC. 

The WebRTC worker annotation path does not perform exactly the same CSV and Streamlit session-state writes as the OpenCV path. 

This is a deliberate architectural distinction related to worker-thread safety. 

The browser processing workflow can therefore be represented as: 

Browser Camera | v WebRTC Worker 

| v Frame Processing | v Annotation | v 

Protected Result State | v 

Streamlit UI 

rather than directly performing every application-state or CSV operation from the worker. 

Consequently, behavior between browser-based processing and stateful OpenCV processing should not automatically be assumed to be identical in every internal operation. 

## **17.2.11 File-Based Storage Limitation** 

The current project uses local files and CSV records for persistence. 

This approach is practical for a local academic project but is not designed for large-scale concurrent distributed production use. 

Potential limitations include: 

- concurrent writes, 

- file-locking concerns, 

- schema evolution, 

- transaction handling, 

- multi-user consistency, 

- backup management, 

- large-scale querying. 

The current architecture therefore remains more appropriate for a local or controlled deployment rather than a distributed production environment with many simultaneous operators. 

## **17.2.12 Hardware and Performance Measurements** 

The current project does not establish measured application-wide values for: 

- RAM usage, 

- CPU utilization, 

- GPU utilization, 

- maximum camera count, 

- operational FPS. 

Therefore, the report must not claim a specific maximum camera capacity or guaranteed real-time FPS. 

The benchmark latency measurements described in Chapter 14 belong to the controlled AI evaluation and should not automatically be treated as complete application performance measurements. 

A proper performance study would require measuring the complete operational application under defined hardware and camera conditions. 

## **17.2.13 Security Limitations** 

The current project contains several security controls, but it does not implement every control expected in a production biometric platform. 

The current limitations include the absence of demonstrated: 

- password hashing, 

- MFA, 

- encryption at rest, 

- TLS configuration within the application, 

- formal retention management, 

- comprehensive security auditing. 

These limitations are important because the system processes sensitive face and location information. 

Therefore, production deployment would require additional security engineering beyond the current academic implementation. 

## **17.2.14 Privacy and Retention Limitation** 

The project does not currently implement a comprehensive automated retention policy. 

Face images, unknown-person records, and event histories can therefore remain in local storage until they are manually managed. 

A production deployment would need explicit policies for: 

- how long data is stored, 

- who can access it, 

- when it is deleted, 

- how deletion is recorded, 

- how backups are handled. 

These requirements are deployment-specific and should be determined before real-world use. 

## **17.2.15 Threat Detection Is Heuristic** 

The current threat-detection mechanism uses image-processing heuristics rather than a separately trained and validated weapon/fire detection model. 

Therefore: 

Heuristic Result ↓ Possible Threat 

does not mean: 

Confirmed Threat 

Similarly: 

Possible Weapon ≠! Verified Weapon 

The system therefore requires human interpretation of such alerts. 

## **17.3 Safe Model-Change Workflow** 

Changing a face-recognition model, detector, metric, or threshold can affect system behavior. 

A model change should therefore not be performed simply because a different model appears stronger in a small experiment. 

The safe workflow should be: 

Current Production Configuration | v Record Baseline | v Prepare Candidate Model | v Separate Enrollment/Test Data | v Add Independent Impostor Dataset | v Run Evaluation | +------+------+ |             | v             v Recognition      False Victim Metrics          Review |             | +------+------+ | 

v Test Real Deployment Conditions | v Measure Latency & Resource Cost | v Human Review | v Change Approved? /       \ Yes        No |          | v          v Update       Retain Configuration  Current Model 

## **17.4 Record the Current Production Configuration** 

Before changing any model or threshold, the existing production configuration should be recorded. 

For example, the current Victim Search production configuration contains specific model, detector, metric, and threshold settings. 

This baseline is important because otherwise it becomes difficult to determine whether a later change actually improved the system. 

The baseline record should include: 

- recognition model, 

- detector, 

- metric, 

- threshold, 

- software environment, 

- relevant runtime availability, 

- dataset version, 

- benchmark configuration. 

## **17.5 Maintain Enrollment/Test Separation** 

A candidate model must be evaluated using independent test data. 

The following structure should be maintained: 

Enrollment Data 

| v Candidate Model | X | X  Do not reuse as test | v 

Independent Test Data 

If the same images are used for both enrollment and testing, the measured performance may not represent generalization to new observations. 

Therefore, enrollment/test separation must remain a core requirement for every future model comparison. 

## **17.6 Include Independent Impostors** 

A candidate model must not be evaluated only on genuine Victim images. 

Independent impostors are required to test whether the candidate incorrectly accepts another person as the Victim. 

The evaluation should therefore contain: 

Genuine Victim + Independent Impostors | v Candidate Model | v TP / TN / FP / FN 

This is particularly important because a model that increases genuine acceptance while also increasing false Victim matches may not provide an acceptable operational change. 

## **17.7 Evaluate Actual Deployment Conditions** 

A model should also be tested under conditions that resemble the intended deployment. 

Relevant conditions include: 

- camera distance, 

- lighting, 

- face angle, 

- blur, 

- occlusion, 

- multiple faces, 

- image resolution, 

- detector availability. 

A model that performs well on clean images may behave differently when used with a surveillance camera. 

Therefore, the model-change workflow should include deployment-representative testing before the configuration is changed. 

## **17.8 Measure Latency and Resource Cost** 

Recognition quality is only one dimension of model selection. 

A candidate model should also be evaluated for: 

- processing latency, 

- throughput, 

- CPU usage, 

- RAM usage, 

- GPU usage where applicable, 

- startup time, 

- model loading cost. 

Conceptually: 

Model Evaluation=Recognition Quality+False Match Analysis+Performance+Resource CostModel\ Evaluation = Recognition\ Quality + False\ Match\ Analysis + Performance + Resource\ Cost 

A model should therefore not be changed solely based on a single metric such as F1. 

## **17.9 Review False Victim Cases** 

False Victim matches require explicit review before a model or threshold change is accepted. 

The workflow should identify: 

- which person was incorrectly accepted, 

- which model produced the result, 

- which threshold was used, 

- the measured distance, 

- detector configuration, 

- environmental condition, 

- whether the error can be reproduced. 

This provides evidence for determining whether a change actually improves the safety of Victim Search. 

## **17.10 Model-Change Decision Principle** 

The model-change workflow should therefore follow an evidence-based principle: 

A candidate model should only replace the current configuration after independent evaluation demonstrates acceptable recognition behavior, false-Victim behavior, deployment compatibility, and computational cost. 

This avoids selecting a model solely because it produced a higher value on one benchmark metric. 

## **17.11 Future Scope** 

The current limitations provide several clear directions for future development. 

### **17.11.1 Larger Victim Dataset** 

The first improvement is to expand the Victim evaluation dataset. 

Future testing should include: 

- more Victim identities, 

- more enrollment images, 

- more independent test images, 

- more impostor identities, 

- more environmental variations. 

This would make the measured results more representative of the intended application. 

## **17.11.2 Larger Staff Dataset** 

A dedicated Staff dataset should be created and evaluated independently. 

The evaluation should measure: 

TP, TN, FP, FNTP,\ TN,\ FP,\ FN 

along with: 

Precision, Recall, F1, FAR, FRRPrecision,\ Recall,\ F1,\ FAR,\ FRR 

This would establish a quantitative baseline for Staff recognition rather than relying only on functional implementation. 

## **17.11.3 Dedicated Unknown Re-ID Evaluation** 

Unknown Re-ID should receive an independent benchmark. 

The dataset could contain several appearances of the same unknown person: 

Camera A → unknown_001 Camera B → unknown_001 Camera C → unknown_001 

along with different individuals: 

Camera A → unknown_002 Camera B → unknown_003 

The evaluation could then determine whether the system correctly maintains identity continuity. 

## **17.11.4 Labeled Video Sequences** 

Future evaluation should include labeled video sequences. 

The planned comparison can include: 

1 Frame ↓ 

Recognition Decision 

3 Frames ↓ Consistency Decision 

5 Frames ↓ Consistency Decision 

Metrics should include: 

- TP, 

- TN, 

- FP, 

- FN, 

- recall, 

- precision, 

- F1, 

- confirmation latency, 

- false-alert frequency. 

This would provide evidence for whether temporal confirmation improves system behavior. 

## **17.11.5 Threshold Calibration** 

Future versions should calibrate thresholds according to: 

- recognition model, 

- detector, 

- camera, 

- environment, 

- image quality. 

The current benchmark demonstrates that threshold changes can alter false-positive behavior. 

Therefore, a single universal threshold should not automatically be assumed to be appropriate for every model and deployment condition. 

## **17.11.6 Database or Transactional Event Store** 

The current file-based architecture could eventually be replaced or supplemented by a database or transactional event store. 

Potential benefits include: 

- structured schema, 

- transaction handling, 

- concurrent access, 

- indexing, 

- query performance, 

- controlled migrations, 

- stronger data integrity. 

A future architecture could therefore evolve from: 

Streamlit | +---- Images 

| +---- CSV Files 

toward: 

Streamlit | v Application/Data Layer | +-------------+ |             | v             v Database       Secure File Storage 

This would be particularly relevant for multi-user or multi-camera deployment. 

## **17.11.7 Stronger Authentication** 

Future versions could add stronger authentication mechanisms such as: 

- password hashing, 

- MFA, 

- external identity provider, 

- centralized role management, 

- persistent authentication auditing. 

This would make the system more appropriate for controlled organizational environments. 

## **17.11.8 Encryption and Privacy Controls** 

Future deployments should consider: 

- encryption at rest, 

- encrypted communication, 

- secure backups, 

- data-retention rules, 

- controlled deletion, 

- consent/notice mechanisms where applicable, 

- detailed privacy auditing. 

These controls are particularly important because N-ONE processes facial and location-related information. 

## **17.11.9 Automated Security Auditing** 

A future version could introduce dedicated security auditing for: 

- login attempts, 

- role changes, 

- profile modifications, 

- model changes, 

- threshold changes, 

- data deletion, 

- configuration changes. 

This would provide a more comprehensive security trail. 

## **17.11.10 Reproducible Performance Testing** 

The project should eventually establish a repeatable performance benchmark covering: 

- CPU usage, 

- RAM usage, 

- GPU usage, 

- latency, 

- FPS, 

- startup time, 

- camera count, 

- resolution, 

- model loading time. 

For example: 

Hardware Configuration + Software Configuration + Camera Configuration | v Performance Benchmark | +---- Latency +---- FPS +---- CPU +---- RAM +---- GPU +---- Camera Scale 

This would allow future changes to be compared objectively. 

## **17.11.11 Automated Browser Testing** 

A future testing framework should include complete browser-level workflows. 

For example: 

Login ↓ Select Role ↓ Register Profile ↓ Select Victim ↓ Start Camera ↓ Run Victim Search ↓ Review Result ↓ Verify Log ↓ Logout 

Such tests would complement the existing unit and behavior tests. 

## **17.11.12 Controlled Deployment Validation** 

Before real deployment, the complete application should be tested under controlled conditions. 

This should include: 

- known camera, 

- defined lighting, 

- controlled subjects, 

- known distances, 

- known network configuration, 

- defined hardware, 

- documented software environment. 

The purpose would be to establish how the actual deployed system behaves rather than relying only on offline benchmark results. 

## **17.11.13 Trained Threat Detection Model** 

The current threat subsystem uses heuristic detection. 

A future version could evaluate a dedicated trained threat-detection model independently from face recognition. 

The future architecture could be: 

Camera Frame 



<!-- Start of picture text -->
     |<br>     +----------------------+<br>     |                      |<br>     v                      v<br>Face Recognition       Threat Detector<br>     |                      |<br>     v                      v<br>Identity Result        Threat Candidate<br>     |                      |<br>     +----------+-----------+<br>                |<br>                v<br>           Human Review<br><!-- End of picture text -->

This would allow face recognition and threat detection to be evaluated using their own datasets and metrics. 

## **17.11.14 Multi-Camera Orchestration** 

Multi-camera operation is a potential future capability, but it should be introduced only after singlecamera behavior has been measured adequately. 

A future architecture might contain: 

Camera 1 ─┐ Camera 2 ─┤ Camera 3 ─┤ Camera 4 ─┘ | v Central Processing | v Identity / Event Correlation | v 

##### Location-Aware History 

However, scaling to multiple cameras would introduce additional requirements such as: 

- concurrency, 

- resource scheduling, 

- event ordering, 

- storage scalability, 

- network reliability, 

- synchronization, 

- camera-specific configuration. 

Therefore, multi-camera orchestration should be considered a future stage rather than an assumed current capability. 

## **17.12 Future Development Roadmap** 

The future work can be organized into progressive stages. 

**Stage Future Work** 

- Phase 1 Resolve current testing/documentation gaps 

- Phase 2 Expand Victim and Staff datasets 

- Phase 3 Benchmark Staff and Unknown Re-ID 

- Phase 4 Add labeled video and multi-frame testing 

- Phase 5 Calibrate model/detector/threshold combinations 

- Phase 6 Measure complete application performance 

- Phase 7 Strengthen authentication and data security 

- Phase 8 Introduce transactional database storage 

- Phase 9 Evaluate trained threat-detection model 

- Phase 10 Controlled multi-camera deployment 

This staged approach reduces the risk of scaling the system before the core single-camera behavior has been sufficiently validated. 

## **17.13 Current System vs Future Scope** 

**Area Current State Future Scope** 

|Victim<br>Recognition|Implemented and benchmarked|Larger, more diverse benchmark|
|---|---|---|
|Staff Recognition|Implemented; accuracy not<br>measured|Dedicated benchmark|
|Unknown Re-ID|Implemented; accuracy not<br>measured|Formal Re-ID evaluation|
|Threat Detection|Heuristic|Dedicated trained detector|
|Multi-frame|Not measured|Labeled video benchmark|
|Model Selection|Benchmark-based|Continuous calibration|
|Storage|Local images + CSV|Transactional database|
|Authentication|Basic application authentication|Strong identity provider/MFA|
|Encryption|Not implemented|Encryption at rest/in transit|
|Retention|Not formalized|Automated retention policy|
|Performance|Benchmark latency available|Full CPU/RAM/GPU/FPS/scale<br>study|
|Browser Testing|Partial behavior tests|Full end-to-end automation|
|Deployment|Controlled/local|Controlled production validation|
|Cameras|Single-camera-oriented<br>workflow|Multi-camera orchestration|



## **17.14 Research Opportunities** 

The limitations of the current system also provide opportunities for further research. 

Potential research questions include: 

#### **Research Question 1** 

How does recognition performance change as the number of enrollment images increases? 

#### **Research Question 2** 

How does the optimal threshold change between different face-recognition models? 

#### **Research Question 3** 

How does camera distance affect Victim recognition? 

#### **Research Question 4** 

Can temporal confirmation reduce false Victim matches without significantly increasing missed detections? 

#### **Research Question 5** 

How does the choice of detector affect recognition latency and recognition quality? 

#### **Research Question 6** 

Can Unknown Re-ID remain reliable across different camera locations? 

#### **Research Question 7** 

What hardware configuration provides an appropriate balance between recognition quality and processing latency? 

These questions can form the basis for future academic work based on the existing N-ONE architecture. 

## **17.15 Overall Assessment of Limitations** 

The limitations identified in this chapter do not invalidate the N-ONE project. 

Instead, they define the boundaries of the evidence currently available. 

The project has demonstrated: 

- a functioning modular application architecture, 

- authentication and role separation, 

- controlled profile registration, 

- target-restricted Victim Search, 

- Unknown Person management, 

- heuristic threat detection, 

- AI model benchmarking, 

- threshold analysis, 

- evaluation data management, 

- testing infrastructure. 

However, the current evidence does not establish: 

- universal face-recognition accuracy, 

- Staff recognition accuracy, 

- Unknown Re-ID accuracy, 

- Threat Detection accuracy, 

- multi-frame performance, 

- maximum camera capacity, 

- guaranteed operational FPS, 

- production-scale concurrency, 

- complete enterprise security. 

Keeping these distinctions visible improves the technical credibility of the project. 

## **17.16 Chapter Conclusion** 

N-ONE provides a functional foundation for AI-assisted Victim Search, Staff recognition, Unknown Person Re-ID, and heuristic threat monitoring. The current implementation and benchmark establish measurable evidence for selected parts of the system, particularly the Victim recognition workflow. 

However, several important limitations remain. The current benchmark is relatively small and primarily image-based. Staff recognition, Unknown Re-ID, Threat Detection, and multi-frame behavior have not yet received independent quantitative evaluation. The OpenCV fallback is not a trained neural identity model, and environmental factors such as lighting, pose, blur, distance, occlusion, and multiple faces remain important challenges. 

The application's local file-based architecture also limits its suitability for concurrent distributed deployment. Similarly, application-wide CPU, RAM, GPU, camera-scale, and operational FPS measurements are not currently established. Security controls such as password hashing, encryption, formal retention, and comprehensive auditing remain future requirements. 

Future development should therefore proceed through **evidence-based incremental improvement** rather than simply adding more features. Model changes should be validated using independent enrollment and test data, independent impostors, deployment-representative conditions, falseVictim review, and computational measurements. 

The long-term scope includes larger datasets, dedicated Staff and Re-ID benchmarks, labeled video evaluation, threshold calibration, stronger security, transactional storage, trained threat detection, automated browser testing, reproducible performance evaluation, and eventually multi-camera orchestration. 

Thus, the current N-ONE implementation should be understood as a **validated academic prototype with a defined path toward broader experimental validation and production-oriented engineering** , rather than as a fully validated large-scale surveillance platform. 

## **CHAPTER 18 – CONCLUSION** 

### **18.1 Introduction** 

N-ONE is an implemented Streamlit-based prototype developed to demonstrate an integrated approach to AI-assisted surveillance, Victim identification, registered-person recognition, Unknown Person Re-ID, and heuristic threat monitoring. 

The project brings together multiple computer-vision workflows within a single application while maintaining explicit boundaries between their purposes. This separation is one of the important architectural characteristics of N-ONE because the system does not treat every detected face or visual event as the same type of problem. 

The project combines: 

- authenticated application access, 

- Administrator and Operator roles, 

- controlled face-only profile enrollment, 

- Victim Search, 

- registered-person recognition, 

- local Unknown Person Re-ID, 

- heuristic threat monitoring, 

- camera/location context, 

- CSV-based event logging, 

- image-based evidence storage, 

- AI model evaluation and threshold analysis. 

The resulting system provides an academic prototype for investigating how these capabilities can be integrated while maintaining clear technical and operational boundaries. 

## **18.2 Integrated System Contribution** 

One of the primary contributions of N-ONE is the integration of multiple computer-vision workflows into a common application. 

The overall conceptual workflow can be represented as: 

N-ONE | +---------------+---------------+ |               |               | v               v               v Victim Search    Registered       Threat Recognition     Monitoring |               |               | v               v               v Selected          Staff /       Heuristic Victim Target     Known User      Analysis 

| +-------------------+ | v Unknown Person Re-ID | v Local Identity Continuity | v CSV / Image Evidence 

The system therefore does not rely on a single recognition workflow for every operational situation. 

## **18.3 Separation of Operational Tasks** 

A major design decision in N-ONE is the explicit separation between different identification and detection tasks. 

### **Victim Search** 

Victim Search is a **selected known-identity workflow** . 

The operator selects a particular Victim profile, and the recognition process is restricted to that target. 

Conceptually: 

Selected Victim | v Target-specific Known Cache | v Face Comparison | +--------+ |        | v        v Match    No Match 

This prevents the Victim Search operation from being treated as an unrestricted search across every registered identity. 

### **Unknown Person Re-ID** 

Unknown Re-ID is a different problem. 

Instead of assigning an unknown person a confirmed real-world identity, N-ONE maintains a local identifier such as: 

unknown_001 

Later observations can be associated with the same locally maintained record when the system determines that they correspond to the same unknown representation. 

Therefore: 

Unknown ID≠!Confirmed Real IdentityUnknown\ ID \neq Confirmed\ Real\ Identity 

This distinction is important both technically and ethically. 

### **Threat Detection** 

Threat Detection operates independently of face recognition. 

It uses a heuristic image-processing path rather than treating face-recognition models as weapon or threat detectors. 

Therefore: 

Face Recognition 

≠! 

Threat Detection 

This architectural separation reduces the risk of incorrectly presenting a face-recognition result as evidence of a threat. 

## **18.4 Profile Enrollment and Identity Management** 

N-ONE includes a controlled profile-enrollment workflow. 

The system requires an appropriate face input during registration and maintains separate profile categories such as: 

- Staff, 

- ● Victim. 

The enrollment workflow provides a controlled source of known identities for later recognition. 

Multiple face-angle images can also be associated with a profile, allowing the known-face representation to include more than one view. 

This is important because recognition performance can be affected by changes in: 

- face angle, 

- pose, 

- illumination, 

- distance, 

- image quality. 

The profile-management system therefore provides the foundation on which the later recognition workflow operates. 

## **18.5 Victim Search Contribution** 

The Victim Search workflow represents one of the central functional components of N-ONE. 

Instead of simply asking: 

“Which registered person is this?” 

the system allows the operator to specify: 

“Is the selected Victim present in this camera/source?” 

This changes the operational problem from unrestricted identity classification to target-specific search. 

The workflow combines: 

1. Victim profile selection, 

2. target-specific known-face filtering, 

3. face detection, 

4. representation generation, 

5. distance calculation, 

6. threshold-based decision, 

7. camera-location context, 

8. result presentation, 

9. sighting logging. 

When the selected Victim is matched, the system can present information such as: 

- Victim identity, 

- profile information, 

- camera location, 

- recognition distance, 

- timestamp, 

- model/backend information, 

- sighting history. 

This makes the result more useful for investigation and review than an isolated recognition label. 

## **18.6 AI Benchmark Contribution** 

The project also includes a dedicated evaluation process for comparing recognition models. 

The benchmark evaluates: 

- FaceNet, 

- FaceNet512, 

- ArcFace. 

The comparison uses cosine distance and evaluates genuine Victim and impostor trials. 

The benchmark therefore provides quantitative evidence rather than relying solely on visual demonstrations. 

At threshold: 

τ=0.40\tau = 0.40 

the measured results were: 

|**Metric**|**FaceNet**|**FaceNet512**|**ArcFace**|
|---|---|---|---|
|TP|21|22|23|
|TN|60|60|60|
|FP|0|0|0|
|FN|11|10|9|
|Precision|1.0000|1.0000|1.0000|
|Recall|0.65625|0.68750|0.71875|
|F1|0.79245|0.81481|0.83636|
|FAR|0|0|0|
|FRR|0.34375|0.31250|0.28125|



Within the limited evaluated sample, ArcFace produced the highest measured recall and F1 among the three tested models at this threshold. 

However, this result is strictly an experimental benchmark observation. 

It should not be interpreted as proof that ArcFace will always outperform the other models in every environment. 

## **18.7 False Victim Match Analysis** 

An important result of the benchmark is that at threshold 0.40: 

FP=0FP=0 

for all three evaluated models within the available negative trials. 

This means that no incorrect Victim match was observed among those tested impostor trials. 

This is an important experimental observation because false Victim identification is a critical failure mode for a target-specific Victim Search system. 

However, zero observed false positives in a limited dataset does not mean: 

FAR=0FAR=0 

for every possible future dataset or deployment. 

The correct interpretation is: 

No false Victim matches were observed in the evaluated negative trials under the specified benchmark conditions. 

This distinction maintains the scientific validity of the result. 

## **18.8 Production Configuration and Benchmark Configuration** 

The project maintains an important distinction between the configuration used by the live application and the configuration used during controlled benchmarking. 

The current live Victim Search source configuration is: 

##### **Parameter Current Production Configuration** 

Recognition model FaceNet Detector OpenCV Metric Cosine 

Threshold 

0.40 

The controlled benchmark evaluated: 

**Parameter Benchmark Configuration** 

Recognition models FaceNet, FaceNet512, ArcFace Detector RetinaFace where supported Metric Cosine Main threshold 0.40 

Therefore, the benchmark result for ArcFace should not be described as meaning that the current production N-ONE application is running ArcFace as its default Victim Search model. 

The distinction between **experimental benchmark configuration** and **current application configuration** is an important part of the project's technical documentation. 

## **18.9 OpenCV Fallback** 

N-ONE also provides a lightweight OpenCV-based fallback when the neural recognition runtime is unavailable. 

The fallback provides an alternative computer-vision processing path, but it is not equivalent to a trained neural identity-recognition model. 

Therefore, the project maintains the following conceptual boundary: 

TensorFlow / Neural Runtime | v Neural Recognition Models | v Identity Representation | v 

Similarity Matching 

Neural Runtime Unavailable | 

v OpenCV Fallback | 

v 

Limited Face Processing 

This fallback architecture improves runtime flexibility while preventing unsupported claims about neural identity recognition when the required neural environment is unavailable. 

## **18.10 Evidence and Logging** 

Another contribution of N-ONE is its use of local image and CSV evidence storage. 

The system can maintain information related to: 

- registered profiles, 

- unknown-person records, 

- Victim sightings, 

- locations, 

- timestamps, 

- audit-related events. 

This creates a basic evidence trail that can be reviewed after recognition events. 

The location-aware Victim workflow is particularly useful because a recognition result can be associated with the camera context supplied by the operator. 

The conceptual flow is: 

Face Observation | v Recognition Decision | 

v Identity / Unknown Result | v Camera Location | v Timestamp | v 

Stored Sighting Record 

This converts an isolated frame-level result into a reviewable event. 

## **18.11 Security and Privacy Contribution** 

The project also incorporates several security-aware design decisions. 

These include: 

- authentication, 

- Administrator/Operator separation, 

- failed-login lockout, 

- protected administrative controls, 

- secret configuration outside source code, 

- controlled profile management, 

- restricted Victim target selection. 

At the same time, the project explicitly identifies its security limitations. 

The current implementation does not establish: 

- password hashing, 

- MFA, 

- encryption at rest, 

- formal retention management, 

- comprehensive production security auditing. 

Therefore, N-ONE should be understood as an academic prototype with security-aware controls rather than a complete production-grade biometric security platform. 

## **18.12 Ethical Design Considerations** 

Because the system processes facial information, responsible interpretation is an important part of the project. 

Three principles are particularly important. 

#### **1. Match distance is not percentage certainty** 

A cosine distance and threshold determine whether the configured matching rule is satisfied. 

It should not automatically be converted into a statement such as: 

“The system is 95% certain this is the Victim.” 

Such a probability interpretation would require separate calibration evidence. 

#### **2. Unknown ID is not real identity** 

An internal identifier such as: 

unknown_004 

does not establish the person's real identity. 

#### **3. Possible threat is not confirmed threat** 

A heuristic result such as: 

Possible weapon 

should not be interpreted as proof that a weapon is present. 

Human review remains important for significant operational decisions. 

## **18.13 Current Limitations** 

The project also demonstrates the importance of clearly documenting what has **not** been measured. 

The current evidence does not establish quantitative performance for: 

- Staff recognition, 

- Unknown Re-ID, 

- Threat Detection, 

- multi-frame confirmation. 

Similarly, the project does not currently establish measured: 

- maximum camera capacity, 

- complete application FPS, 

- application RAM usage, 

- application CPU utilization, 

- GPU utilization. 

The Victim benchmark itself is limited in size and is primarily based on still images. 

These limitations prevent the project from making universal performance claims. 

## **18.14 Academic and Research Value** 

N-ONE has value beyond simply providing a working interface. 

The project demonstrates several important software and AI engineering concepts: 

- modular computer-vision processing, 

- role-based application access, 

- controlled identity enrollment, 

- target-specific recognition, 

- similarity-based matching, 

- threshold evaluation, 

- false-positive/false-negative analysis, 

- AI model comparison, 

- fallback runtime design, 

- local event logging, 

- dataset management, 

- software testing, 

- security analysis, 

- privacy considerations. 

The benchmark also demonstrates an important research principle: 

A model should be evaluated using measurable evidence rather than selected solely on the basis of assumptions or model popularity. 

This approach makes the project more suitable for academic demonstration and further experimentation. 

## **18.15 Overall Project Outcome** 

The completed N-ONE prototype establishes a common operational framework in which: 

Authentication ↓ Role Selection ↓ Profile Management ↓ Camera / Image Input ↓ Processing Mode | +-------------------+ |         |         | v         v         v Victim    Staff     Threat Search    /Known    Analysis | v Unknown Re-ID | v Evidence / Logs | v Human Review 

This structure demonstrates how different computer-vision capabilities can coexist without being treated as identical tasks. 

## **18.16 Key Technical Findings** 

The project produced several important technical findings. 

#### **Finding 1 — Target restriction is important** 

Victim Search is explicitly restricted to the selected Victim rather than treating every known identity as a valid target. 

#### **Finding 2 — Recognition performance depends on configuration** 

The evaluated models produced different recall and F1 values at the same threshold. 

#### **Finding 3 — Threshold selection matters** 

Changing the threshold changed observed false-positive behavior in the benchmark. 

#### **Finding 4 — Benchmark and production configurations must be separated** 

The benchmark used RetinaFace with multiple neural models, while the current live configuration remains FaceNet with OpenCV. 

#### **Finding 5 — Fallback behavior has a defined boundary** 

The OpenCV fallback is not treated as an equivalent replacement for a neural identity model. 

#### **Finding 6 — Several subsystems require independent evaluation** 

Staff recognition, Unknown Re-ID, Threat Detection, and multi-frame processing cannot be inferred from the Victim benchmark. 

## **18.17 Future Direction** 

The next stage of N-ONE should focus on controlled validation rather than simply increasing the number of features. 

The recommended progression is: 

Larger Independent Dataset ↓ 

Staff / Unknown / Threat Benchmarks ↓ 

Labeled Video Evaluation 

↓ Threshold Calibration ↓ Performance Benchmarking ↓ Security Strengthening ↓ Transactional Storage ↓ Controlled Deployment ↓ Multi-Camera Evaluation 

This approach allows each stage to be validated before introducing additional complexity. 

## **18.18 Final Conclusion** 

N-ONE demonstrates an implemented Streamlit prototype for AI-assisted surveillance and Victim Search that integrates authenticated operation, controlled face-only profile enrollment, targetrestricted Victim Search, registered-person recognition, local Unknown Person Re-ID, heuristic threat monitoring, and CSV/image-based evidence storage. 

A central strength of the project is its explicit separation of operational tasks. **Victim Search** is treated as a selected known-identity search problem, **Unknown Re-ID** as a local continuity problem, and **Threat Detection** as an independent heuristic analysis problem. This separation reduces conceptual ambiguity and makes the individual subsystems easier to evaluate and improve independently. 

The project also contains meaningful experimental evidence for Victim face recognition. At a cosine-distance threshold of **0.40** , the tested FaceNet, FaceNet512, and ArcFace configurations produced zero observed false Victim matches in the available negative trials. Among these configurations, ArcFace produced the highest measured recall and F1 in the evaluated sample. However, these findings are limited to the defined dataset and experimental protocol and should not be interpreted as universal accuracy or guaranteed operational safety. 

The current live Victim Search configuration remains **FaceNet + OpenCV + cosine distance + threshold 0.40** , while the OpenCV fallback provides a lightweight alternative when the neural runtime is unavailable. The distinction between the benchmark configuration and production configuration is therefore maintained explicitly. 

The project also clearly identifies its remaining limitations. Staff recognition, Unknown Re-ID, Threat Detection, and multi-frame performance have not received independent quantitative validation. The current benchmark is relatively small and primarily image-based, while applicationwide resource usage, maximum camera capacity, and operational FPS have not been comprehensively measured. 

Security and privacy controls also require further strengthening before any higher-risk or production deployment. Password hashing, MFA, encryption, formal retention controls, stronger auditing, and more robust data-management mechanisms represent important future improvements. 

Therefore, the principal outcome of N-ONE is not a claim of perfect or universal recognition. Instead, it is a **working, testable, and research-oriented prototype with measurable Victimrecognition evidence, explicit system boundaries, documented limitations, and a defined path toward larger-scale validation** . 

The appropriate next stage is a controlled evaluation program involving larger independent datasets, sequence-level video testing, human review of false Victim cases, stronger identity and storage controls, and reproducible deployment-performance measurements. This approach provides a technically grounded foundation for further development of N-ONE while keeping its current capabilities and limitations clearly distinguishable. 

## **CHAPTER 19 – BIBLIOGRAPHY / REFERENCES** 

### **19.1 Introduction** 

This chapter lists the academic papers, software documentation, dataset references, and internal N- ONE project resources used during development, implementation, testing, and evaluation. 

The references mainly cover: 

- Face Recognition 

- Face Embedding Models 

- Computer Vision 

- Streamlit 

- DeepFace 

- Evaluation Datasets 

- N-ONE Architecture and Implementation 

- Testing and AI Evaluation 

For the final university submission, the references should be formatted according to the **citation style prescribed by AKS University** . Online sources should also include their verified access dates where required. 

### **19.2 Academic References** 

#### **1. FaceNet** 

Schroff, F., Kalenichenko, D., & Philbin, J. (2015). _FaceNet: A Unified Embedding for Face Recognition and Clustering_ . Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR). 

This paper provides the academic foundation for the FaceNet approach used in the N-ONE facerecognition workflow. FaceNet represents faces as numerical embeddings that can be compared using a distance or similarity measure. 

In N-ONE, this concept is used in the general pipeline: 

Face Image ↓ Face Representation ↓ Embedding ↓ Distance Calculation ↓ 

Threshold Decision 

#### **2. ArcFace** 

Deng, J., Guo, J., Xue, N., & Zafeiriou, S. (2019). _ArcFace: Additive Angular Margin Loss for Deep Face Recognition_ . Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR). 

ArcFace is one of the face-recognition models evaluated during the N-ONE benchmark. 

The benchmark compared ArcFace with FaceNet and FaceNet512 using the defined evaluation dataset and cosine-distance-based decision process. 

The benchmark result should be understood as project-specific experimental evidence and not as a universal performance claim for ArcFace. 

### **19.3 Software Documentation** 

#### **3. OpenCV Documentation** 

OpenCV. _OpenCV Documentation – Cascade Classifier and Computer Vision Library Documentation_ . 

##### <u>OpenCV Documentation</u> 

OpenCV is used in N-ONE for computer-vision operations including image processing, face detection, camera/frame processing, and the lightweight fallback processing path. 

#### **4. Streamlit Documentation** 

Streamlit. _Streamlit Documentation_ . 

##### <u>Streamlit Documentation</u> 

Streamlit provides the main application interface for N-ONE, including: 

- authentication interface, 

- Administrator and Operator dashboards, 

- profile registration, 

- Victim Search, 

- camera/source controls, 

- monitoring, 

- result presentation, 

- logs and analytics. 

### **19.4 DeepFace Reference** 

#### **5. DeepFace Project Documentation and Source** 

DeepFace project documentation and source included within the N-ONE repository under: 

deepface/ 

The project integrates DeepFace conditionally through: 

deepface_adapter.py 

The DeepFace integration provides the neural face-recognition path when the required runtime and model dependencies are available. 

The project also maintains an OpenCV-based fallback, so DeepFace availability should not be interpreted as a requirement for every N-ONE execution environment. 

### **19.5 Dataset Reference** 

#### **6. Labeled Faces in the Wild (LFW)** 

The N-ONE evaluation workspace records LFW as a source for impostor evaluation data. 

The source information is maintained in: 

evaluation/impostor_sources.csv 

The file preserves source references and a terms note. 

Before final publication or redistribution, the applicable dataset terms should be reviewed again. 

The presence of a dataset source reference does not by itself establish legal compliance for every possible publication or redistribution scenario. 

### **19.6 N-ONE Internal Documentation** 

#### **7. N-ONE Project Documentation** 

The following internal documents are important sources for understanding the actual N-ONE implementation: 

README.md BRAIN.md ARCHITECTURE.md AI_MODEL_CONFIGURATION.md docs/AI_MODEL_EVALUATION_REPORT.md docs/AI_MODELS_AND_CONFIGURATION_GUIDE.md 

These documents provide project-specific information related to: 

- system architecture, 

- project objectives, 

- module design, 

- AI model configuration, 

- evaluation methodology, 

- runtime behavior, 

- limitations, 

- design decisions. 

These internal documents should be treated as implementation evidence rather than external academic references. 

### **19.7 N-ONE Source Code and Testing References** 

#### **8. N-ONE Source and Test Resources** 

Important project implementation resources include: 

app.py deepface_adapter.py evaluation/scripts/ tests/ 

#### **app.py** 

Contains the primary Streamlit application and provides implementation evidence for: 

- authentication, 

- role management, 

- profile registration, 

- Victim Search, 

- recognition workflows, 

- Unknown Re-ID, 

- threat processing, 

- logging, 

- dashboard functionality. 

**deepface_adapter.py** 

Provides the integration boundary between the application and the optional neural face-recognition runtime. 

#### **evaluation/scripts/** 

Contains scripts associated with: 

- dataset processing, 

- model comparison, 

- threshold evaluation, 

- performance measurement, 

- benchmark generation. 

#### **tests/** 

Contains automated tests covering various application behaviors and boundary conditions. 

### **19.8 Reference-to-Project Mapping** 

|**Reference**|**Relevance to N-ONE**|
|---|---|
|Schroff et al. (2015)|FaceNet and face embeddings|
|Deng et al. (2019)|ArcFace recognition model|
|OpenCV Documentation|Computer vision and fallback processing|
|Streamlit Documentation|Application interface|
|DeepFace|Conditional neural recognition integration|
|LFW|Impostor/evaluation dataset|
|N-ONE internal documentation|Architecture and configuration|
|N-ONE source/tests|Implementation and testing evidence|



### **19.9 External References and Internal Evidence** 

It is important to distinguish external references from N-ONE's own evidence. 

#### **External References** 

These provide the technical foundation: 

- FaceNet, 

- ArcFace, 

- OpenCV, 

- Streamlit, 

- DeepFace, 

- LFW. 

#### **Internal Evidence** 

These establish what the N-ONE project actually implements: 

- source code, 

- evaluation scripts, 

- benchmark result files, 

- test files, 

- project documentation. 

For example, the FaceNet paper can support an explanation of the FaceNet approach, but it cannot establish the recall achieved by N-ONE. That recall must come from the project's own benchmark. 

Similarly, Streamlit documentation describes the framework, while the N-ONE source code establishes which Streamlit functionality was actually implemented. 

### **19.10 Recommended Final Reference List** 

For the final project report, the bibliography can be presented as: 

1. Schroff, F., Kalenichenko, D., & Philbin, J. (2015). _FaceNet: A Unified Embedding for Face Recognition and Clustering_ . Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR). 

2. Deng, J., Guo, J., Xue, N., & Zafeiriou, S. (2019). _ArcFace: Additive Angular Margin Loss for Deep Face Recognition_ . Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR). 

3. OpenCV. _OpenCV Documentation – Cascade Classifier and Computer Vision Library Documentation_ . Official OpenCV Documentation 

4. Streamlit. _Streamlit Documentation_ . Official Streamlit Documentation 

5. DeepFace. _DeepFace Project Documentation and Source_ . N-ONE repository, conditionally integrated through deepface_adapter.py. 

6. Labeled Faces in the Wild (LFW). Dataset source and terms information recorded in evaluation/impostor_sources.csv. 

7. N-ONE Project Documentation. README.md, BRAIN.md, ARCHITECTURE.md, AI_MODEL_CONFIGURATION.md, docs/AI_MODEL_EVALUATION_REPORT.md, and docs/AI_MODELS_AND_CONFIGURATION_GUIDE.md. 

8. N-ONE Source Code and Testing Resources. app.py, deepface_adapter.py, evaluation/scripts/, and tests/. 

### **19.11 Final Reference Verification** 

Before final submission, the bibliography should be checked for: 

- correct author names, 

- publication year, 

- paper title, 

- conference/journal name, 

- required publication details, 

- correct official URLs, 

- dataset attribution, 

- access dates, 

- consistency with in-text citations, 

- compliance with the university's required citation style. 

For online references, the final report should use the actual date on which the source was accessed. 

The final verification process can be represented as: 

Reference ↓ Verify Author / Organization ↓ Verify Title ↓ Verify Publication / Documentation ↓ Verify URL / Repository ↓ Add Access Date ↓ Check Citation Style ↓ Final Bibliography 

### **19.12 Chapter Conclusion** 

The bibliography of N-ONE combines academic research, official software documentation, dataset references, and project-specific implementation evidence. 

The FaceNet and ArcFace publications provide the academic foundation for the face-recognition models evaluated in the project. OpenCV and Streamlit documentation support the computer-vision and application framework components, while DeepFace represents the conditional neural recognition integration. 

The LFW reference provides traceability for the external impostor data used during evaluation. The internal N-ONE documentation, source code, evaluation scripts, and test suite provide evidence for the actual implementation and experimental results. 

For the final AKS University submission, all references should be reformatted according to the university's required citation style, online access dates should be verified, and dataset terms should be reviewed before publication or redistribution. 

This ensures that the final report maintains **academic traceability, technical accuracy, and a clear distinction between external research, project implementation, and experimentally measured results** . 

