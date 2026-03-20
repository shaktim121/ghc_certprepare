document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        const participantsHtml = details.participants && details.participants.length > 0
          ? `
              <p><strong>Participants:</strong></p>
              <ul class="participant-list" aria-label="participants for ${name}">
                ${details.participants.map((participant) => `
                  <li class="participant-item" data-participant="${participant}">
                    <span class="participant-name">${participant}</span>
                    <button class="remove-participant" type="button" aria-label="Remove ${participant}">&#x2716;</button>
                  </li>
                `).join("")}
              </ul>
            `
          : `<p><strong>Participants:</strong> <span class="text-muted">No one signed up yet</span></p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${participantsHtml}
        `;

        activitiesList.appendChild(activityCard);

        // Attach delete handlers for each participant
        activityCard.querySelectorAll(".remove-participant").forEach((btn) => {
          btn.addEventListener("click", async () => {
            const participantEmail = btn.closest(".participant-item").dataset.participant;

            const confirmed = window.confirm(`Are you sure you want to remove ${participantEmail} from ${name}?`);
            if (!confirmed) return;

            try {
              const response = await fetch(
                `/activities/${encodeURIComponent(name)}/participants/${encodeURIComponent(participantEmail)}`,
                { method: "DELETE" }
              );

              const result = await response.json();

              if (response.ok) {
                messageDiv.innerHTML = `Removed ${participantEmail} successfully. <button id="undo-button" class="undo-btn" type="button">↩️ Undo</button>`;
                messageDiv.className = "success";

                const undoButton = messageDiv.querySelector("#undo-button");
                let undoPressed = false;

                undoButton.addEventListener("click", async () => {
                  if (undoPressed) return;
                  undoPressed = true;

                  try {
                    const undoResponse = await fetch(
                      `/activities/${encodeURIComponent(name)}/signup?email=${encodeURIComponent(participantEmail)}`,
                      { method: "POST" }
                    );
                    const undoResult = await undoResponse.json();

                    if (undoResponse.ok) {
                      messageDiv.textContent = `Undo successful: ${participantEmail} re-added.`;
                      messageDiv.className = "info";
                      fetchActivities();
                    } else {
                      messageDiv.textContent = undoResult.detail || "Unable to undo removal.";
                      messageDiv.className = "error";
                    }
                  } catch (err) {
                    messageDiv.textContent = "Unable to undo removal. Please try again.";
                    messageDiv.className = "error";
                    console.error("Error undoing participant removal:", err);
                  }

                  setTimeout(() => messageDiv.classList.add("hidden"), 5000);
                });

                fetchActivities();
              } else {
                messageDiv.textContent = result.detail || "Unable to remove participant";
                messageDiv.className = "error";
              }
            } catch (error) {
              messageDiv.textContent = "Unable to remove participant. Please try again.";
              messageDiv.className = "error";
              console.error("Error removing participant:", error);
            }

            messageDiv.classList.remove("hidden");
            setTimeout(() => messageDiv.classList.add("hidden"), 5000);
          });
        });

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
