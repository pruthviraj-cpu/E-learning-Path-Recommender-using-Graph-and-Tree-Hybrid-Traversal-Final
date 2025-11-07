export async function logUserActivity(
  userId: number,
  actionType: string,
  description: string,
  duration: number
): Promise<void> {
  try {
    const response = await fetch(`http://localhost:8000/activity/${userId}/log`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action_type: actionType,
        description: description,
        duration_seconds: duration
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to log activity: ${response.statusText}`);
    }

    const data = await response.json();
    console.log("✅ Activity logged:", data);
  } catch (err) {
    console.error("❌ Error logging activity:", err);
  }
}
