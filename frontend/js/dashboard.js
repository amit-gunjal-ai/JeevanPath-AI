const API_BASE_URL = "http://127.0.0.1:8000";

/* =========================================================
   API
========================================================= */

async function getRecommendations(transcript) {
    const response = await fetch(
        `${API_BASE_URL}/recommend-from-transcript`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                transcript: transcript
            })
        }
    );

    if (!response.ok) {
        throw new Error(
            `Recommendation API failed: ${response.status}`
        );
    }

    return await response.json();
}


/* =========================================================
   LANGUAGE HELPERS
========================================================= */

function formatValue(value) {
    if (!value) {
        return "";
    }

    return String(value)
        .replace(/_/g, " ")
        .replace(/\b\w/g, char => char.toUpperCase());
}


function translateEmploymentPreference(value) {
    if (!value) {
        return "";
    }

    const keyMap = {
        wage_employment: "wageEmployment",
        self_employment: "selfEmployment",
        both: "bothEmployment"
    };

    const key = keyMap[value];

    return key ? t(key) : formatValue(value);
}


function translateMobility(value) {
    if (!value) {
        return "";
    }

    const keyMap = {
        local_only: "localOnly",
        regional: "regional",
        national: "national"
    };

    const key = keyMap[value];

    return key ? t(key) : formatValue(value);
}


/* =========================================================
   PROFILE
========================================================= */

function renderProfile(profile) {
    if (!profile) {
        return `
            <div class="profile-row">
                ${t("noInput")}
            </div>
        `;
    }

    const parts = [];

    if (profile.education_level) {
        parts.push(`
            <div class="profile-row">
                <strong>${t("education")}:</strong>
                ${t("class")} ${profile.education_level}
            </div>
        `);
    }

    if (profile.employment_preference) {
        parts.push(`
            <div class="profile-row">
                <strong>${t("prefers")}:</strong>
                ${translateEmploymentPreference(
                    profile.employment_preference
                )}
            </div>
        `);
    }

    if (profile.mobility) {
        parts.push(`
            <div class="profile-row">
                <strong>${t("mobility")}:</strong>
                ${translateMobility(profile.mobility)}
            </div>
        `);
    }

    if (
        profile.interests &&
        profile.interests.length
    ) {
        parts.push(`
            <div class="profile-row">
                <strong>${t("interests")}:</strong>
                ${profile.interests.join(", ")}
            </div>
        `);
    }

    if (
        profile.skills &&
        profile.skills.length
    ) {
        parts.push(`
            <div class="profile-row">
                <strong>${t("skills")}:</strong>
                ${profile.skills.join(", ")}
            </div>
        `);
    }

    if (!parts.length) {
        return `
            <div class="profile-row">
                ${t("noInput")}
            </div>
        `;
    }

    return parts.join("");
}


/* =========================================================
   RECOMMENDATIONS
========================================================= */

function renderRecommendations(recommendations) {
    if (
        !recommendations ||
        !recommendations.length
    ) {
        return `
            <p class="profile-row">
                ${t("noRecommendations")}
            </p>
        `;
    }

    return recommendations.map(r => {

        const verifiedText =
            r.verified
                ? t("verifiedData")
                : t("prototypeData");

        const missingSkills =
            r.missing_skills &&
            r.missing_skills.length
                ? `
                    <p class="rec-missing">
                        <strong>
                            ${t("toLearn")}:
                        </strong>
                        ${r.missing_skills.join(", ")}
                    </p>
                `
                : "";

        return `
            <div class="rec-card">

                <div class="rec-header">

                    <h4>
                        ${r.pathway_name || ""}
                    </h4>

                    <span class="rec-score">
                        ${r.score ?? 0}%
                    </span>

                </div>

                <p class="rec-category">
                    ${r.category || ""}
                    ·
                    ${verifiedText}
                </p>

                <p class="rec-explanation">
                    ${String(
                        r.explanation || ""
                    ).replace(
                        /\n/g,
                        "<br>"
                    )}
                </p>

                ${missingSkills}

            </div>
        `;

    }).join("");
}


/* =========================================================
   ROADMAP
========================================================= */

function renderRoadmap(roadmap) {
    if (!roadmap) {
        return "";
    }

    const steps = roadmap.roadmap || [];

    return `
        <h3>
            ${t("roadmapFor")}:
            ${roadmap.pathway_name || ""}
        </h3>

        <ol class="roadmap-list">

            ${
                steps.length
                    ? steps.map(
                        (step, index) => `
                            <li>

                                <strong>
                                    ${t("roadmapStep")}
                                    ${index + 1}:
                                    ${step.title || ""}
                                </strong>

                                <br>

                                ${step.detail || ""}

                            </li>
                        `
                    ).join("")
                    : `
                        <li>
                            ${t("noRoadmap")}
                        </li>
                    `
            }

        </ol>
    `;
}


/* =========================================================
   SHOW RESULTS
========================================================= */

function displayResults(data) {

    const profileSummary =
        document.getElementById(
            "profileSummary"
        );

    const recommendationsList =
        document.getElementById(
            "recommendationsList"
        );

    const roadmapSection =
        document.getElementById(
            "roadmapSection"
        );

    const resultsSection =
        document.getElementById(
            "resultsSection"
        );


    if (
        !profileSummary ||
        !recommendationsList ||
        !roadmapSection ||
        !resultsSection
    ) {
        console.error(
            "Required dashboard elements are missing."
        );

        return;
    }


    profileSummary.innerHTML =
        renderProfile(data.profile);


    recommendationsList.innerHTML =
        renderRecommendations(
            data.recommendations
        );


    roadmapSection.innerHTML =
        renderRoadmap(
            data.roadmap_for_top_pick
        );


    resultsSection.style.display =
        "block";


    resultsSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


/* =========================================================
   TEXT PROFILE FORM
========================================================= */

const profileForm =
    document.getElementById("profileForm");


if (profileForm) {

    profileForm.addEventListener(
        "submit",
        async function (e) {

            e.preventDefault();


            const transcriptElement =
                document.getElementById(
                    "transcriptInput"
                );


            const statusText =
                document.getElementById(
                    "statusText"
                );


            const resultsSection =
                document.getElementById(
                    "resultsSection"
                );


            if (!transcriptElement) {
                console.error(
                    "transcriptInput element not found."
                );

                return;
            }


            const transcript =
                transcriptElement.value.trim();


            if (!transcript) {

                statusText.innerText =
                    t("noInput");

                return;
            }


            statusText.innerText =
                t("analyzing");


            resultsSection.style.display =
                "none";


            try {

                const data =
                    await getRecommendations(
                        transcript
                    );


                displayResults(data);


                statusText.innerText = "";


            } catch (error) {

                console.error(error);


                statusText.innerText =
                    t("errorBackend");
            }

        }
    );
}


/* =========================================================
   VOICE RECORDING
========================================================= */

let mediaRecorder = null;
let audioChunks = [];
let mediaStream = null;
let isRecording = false;

/* =========================================================
   START RECORDING
========================================================= */

async function startRecording() {

    try {

        const stream =
            await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
        
        mediaStream = stream;


        mediaRecorder =
            new MediaRecorder(
                stream,
                {
                    mimeType:
                        "audio/webm;codecs=opus",

                    audioBitsPerSecond:
                        128000
                }
            );


        audioChunks = [];


        mediaRecorder.ondataavailable =
            event => {

                if (event.data.size > 0) {

                    audioChunks.push(
                        event.data
                    );
                }
            };


        mediaRecorder.onstop =
            handleRecordingStop;


        mediaRecorder.start();
        isRecording = true;

        const btn = document.getElementById("recordBtn");
        btn.innerHTML = `⏹ ${t("stopRecording")}`;
        document.getElementById("statusText").innerText = t("recording");

    } catch (error) {

        console.error(error);


        document.getElementById(
            "statusText"
        ).innerText =
            t("errorVoice");
    }
}


/* =========================================================
   STOP RECORDING
========================================================= */

function stopRecording() {

    if (
        !mediaRecorder ||
        mediaRecorder.state === "inactive"
    ) {
        return;
    }

    isRecording = false;
    mediaRecorder.stop();


    const btn =
        document.getElementById(
            "recordBtn"
        );


    btn.innerHTML =
        `⏳ ${t("processingVoice")}`;


    btn.disabled = true;


    document.getElementById(
        "statusText"
    ).innerText =
        t("processingVoice");
}


/* =========================================================
   PROCESS VOICE
========================================================= */

async function handleRecordingStop() {

    const audioBlob =
        new Blob(
            audioChunks,
            {
                type: "audio/webm"
            }
        );


    const statusText =
        document.getElementById(
            "statusText"
        );


    const btn =
        document.getElementById(
            "recordBtn"
        );


    const formData =
        new FormData();


    formData.append(
        "audio",
        audioBlob,
        "recording.webm"
    );


    try {

        const response =
            await fetch(
                `${API_BASE_URL}/recommend-from-voice`,
                {
                    method: "POST",
                    body: formData
                }
            );


        if (!response.ok) {

            throw new Error(
                `Voice API failed: ${response.status}`
            );
        }


        const data =
            await response.json();


        const heardText =
            document.getElementById(
                "heardText"
            );


        if (
            heardText &&
            data.translated_text
        ) {

            heardText.innerHTML = `
                <p>
                    <strong>
                        ${t("understoodAs")}:
                    </strong>
                    ${data.translated_text}
                </p>
            `;
        }


        displayResults(data);


        statusText.innerText = "";


    } catch (error) {

        console.error(error);


        statusText.innerText =
            t("errorVoice");


    } finally {
        if (mediaStream) {
            mediaStream.getTracks().forEach(track => track.stop());
            mediaStream = null;
        }

        btn.innerHTML = `🎤 ${t("recordVoice")}`;
        btn.disabled = false;
    }
}


/* =========================================================
   VOICE BUTTON
========================================================= */

const recordBtn =
    document.getElementById(
        "recordBtn"
    );


if (recordBtn) {

    recordBtn.addEventListener(
        "click",
        function () {
            if (isRecording) {
                stopRecording();
            } else {
                startRecording();
            }
        }
    );
}