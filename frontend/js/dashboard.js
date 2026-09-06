const API_BASE_URL = "http://127.0.0.1:8000";

async function getRecommendations(transcript) {
    const response = await fetch(`${API_BASE_URL}/recommend-from-transcript`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript })
    });
    return await response.json();
}

function renderProfile(profile) {
    const parts = [];
    if (profile.education_level) parts.push(`Education: Class ${profile.education_level}`);
    if (profile.employment_preference) parts.push(`Prefers: ${profile.employment_preference.replace("_", " ")}`);
    if (profile.mobility) parts.push(`Mobility: ${profile.mobility.replace(/_/g, " ")}`);
    if (profile.interests && profile.interests.length) parts.push(`Interests: ${profile.interests.join(", ")}`);
    if (profile.skills && profile.skills.length) parts.push(`Skills: ${profile.skills.join(", ")}`);
    return parts.map(p => `<p>${p}</p>`).join("");
}

function renderRecommendations(recommendations) {
    return recommendations.map(r => `
        <div class="rec-card">
            <div class="rec-header">
                <h4>${r.pathway_name}</h4>
                <span class="rec-score">${r.score}%</span>
            </div>
            <p class="rec-category">${r.category}${r.verified ? "" : " · unverified prototype data"}</p>
            <p class="rec-explanation">${r.explanation.replace(/\n/g, "<br>")}</p>
            ${r.missing_skills.length ? `<p class="rec-missing"><strong>To learn:</strong> ${r.missing_skills.join(", ")}</p>` : ""}
        </div>
    `).join("");
}

function renderRoadmap(roadmap) {
    if (!roadmap) return "";
    return `
        <h3>Your Roadmap: ${roadmap.pathway_name}</h3>
        <ol class="roadmap-list">
            ${roadmap.roadmap.map(step => `<li><strong>${step.title}</strong><br>${step.detail}</li>`).join("")}
        </ol>
    `;
}

document.getElementById("profileForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const transcript = document.getElementById("transcriptInput").value.trim();
    if (!transcript) return;

    const resultsSection = document.getElementById("resultsSection");
    const statusText = document.getElementById("statusText");

    statusText.innerText = "Analyzing your profile...";
    resultsSection.style.display = "none";

    try {
        const data = await getRecommendations(transcript);

        document.getElementById("profileSummary").innerHTML = renderProfile(data.profile);
        document.getElementById("recommendationsList").innerHTML = renderRecommendations(data.recommendations);
        document.getElementById("roadmapSection").innerHTML = renderRoadmap(data.roadmap_for_top_pick);

        resultsSection.style.display = "block";
        statusText.innerText = "";
    } catch (err) {
        statusText.innerText = "Something went wrong. Is the backend running?";
        console.error(err);
    }
});