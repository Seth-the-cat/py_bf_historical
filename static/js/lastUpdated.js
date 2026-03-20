const lastUpdated = new Date("{{last_updated}}");
                function updateLastUpdated() {
                    const now = new Date();
                    const diffMs = now - lastUpdated;
                    const diffMins = Math.floor(diffMs / 60000);
                    const diffSecs = Math.floor((diffMs % 60000) / 1000);
                    let displayText = "Last updated ";
                    if (diffMins >= 10 & diffMins < 11) {
                        location.reload();
                    } if (diffMins > 11) {
                        displayText += `${diffMins} minutes ago. ⚠️ Stats fetching likely down. Contact seththecat.`;
                    } if (diffMins > 0) {
                        displayText += `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
                    } else {
                        displayText += `${diffSecs} second${diffSecs !== 1 ? 's' : ''} ago`;
                    }
                    document.getElementById("last_update").innerText = displayText;
                }
                setInterval(updateLastUpdated, 1000);
                updateLastUpdated();