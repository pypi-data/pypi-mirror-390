/**
 * Format duration with appropriate units (ms, s, m, h)
 * @param {number} seconds - Duration in seconds
 * @returns {string} Formatted duration string
 */
function formatDuration(seconds) {
    if (seconds == null || isNaN(seconds)) return "-";

    // Less than 1 second: show milliseconds
    if (seconds < 1) {
        const ms = Math.round(seconds * 1000);
        return `${ms} ms`;
    }

    // Less than 60 seconds: show seconds with 2 decimals
    if (seconds < 60) {
        return `${seconds.toFixed(2)} s`;
    }

    // Less than 1 hour: show minutes and seconds
    if (seconds < 3600) {
        const minutes = Math.floor(seconds / 60);
        const secs = Math.round(seconds % 60);
        return `${minutes} m ${secs} s`;
    }

    // Less than 1 day: show hours, minutes, and seconds
    if (seconds < 86400) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.round(seconds % 60);
        return `${hours} h ${minutes} m ${secs} s`;
    }

    // 1 day or more: show days and hours
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    return `${days} d ${hours} h`;
}

// Function to submit tasks to the task system
async function submitTask(taskFunction, taskName, taskParams) {
    const response = await fetch(window.global_var['task_submit_url'], {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            function: taskFunction,
            name: taskName,
            kwargs: taskParams
        })
    });

    return await response.json();
}