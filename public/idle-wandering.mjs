export const IDLE_WANDER_INTERVAL = 32;

export const ACTIVITY_LABELS = {
  lounge: "🛋️ Santai di lounge",
  water: "🚰 Ambil air galon",
  bakso: "🍜 Jajan bakso",
  coffee: "☕ Ngopi",
  flag: "🇮🇩 Cek flag",
  bookshelf: "📚 Baca di bookshelf",
  pingpong: "🏓 Main ping pong",
  arcade: "🎮 Main game",
  meeting: "👥 Diskusi di meeting",
  bedroom: "🛏️ Istirahat di bedroom",
  lesehan: "🧺 Duduk di lesehan",
  balcony: "🌤️ Menepi di balkon",
  stroll: "🚶 Jalan-jalan"
};

export const ACTIVITY_SPOTS = {
  lounge: [[3.0, 1.8], [3.0, 3.0]],
  water: [[7.3, 1.0], [7.3, 3.0]],
  bakso: [[-14.0, -1.0], [-14.0, 0.5]],
  coffee: [[-6.8, 8.2], [-5.2, 8.2]],
  flag: [[-13.8, 2.0], [-13.8, 3.3]],
  bookshelf: [[-4.2, -7.7], [-2.8, -7.7]],
  pingpong: [[-9.2, -5.5], [-6.8, -5.5]],
  arcade: [[7.4, -5.5], [8.6, -5.5]],
  meeting: [[2.2, 7.0], [-2.2, 7.0], [0, 10.5], [1.5, 9.5], [-1.5, 9.5]],
  bedroom: [[-9.5, 7], [-9.5, 9], [-10.5, 5], [-10.5, 9]],
  lesehan: [[1.0, -2.0], [5.5, -2.0]],
  balcony: [[-2.0, 9.5], [4.0, 9.5]],
  stroll: [[-1.5, -0.5], [1.5, -0.5], [0, 2.5]]
};

const IDLE_ACTIVITY_ORDER = Object.keys(ACTIVITY_SPOTS).filter(name => name !== "stroll");

export function activityLabel(activity) {
  return ACTIVITY_LABELS[activity] || ACTIVITY_LABELS.stroll;
}

export function nextWanderAt(time, status, random = Math.random) {
  return status === "idle" || status === "recent" ? time + IDLE_WANDER_INTERVAL : Infinity;
}

export function chooseActivityTarget(status, random = Math.random, spotRandom = Math.random) {
  if (status === "working") return { activity: "desk", target: null };
  if (status === "chat") {
    const pool = ACTIVITY_SPOTS.meeting;
    return { activity: "meeting", target: pool[Math.floor(spotRandom() * pool.length)] };
  }
  const activity = IDLE_ACTIVITY_ORDER[Math.min(IDLE_ACTIVITY_ORDER.length - 1, Math.floor(random() * IDLE_ACTIVITY_ORDER.length))];
  const pool = ACTIVITY_SPOTS[activity];
  return { activity, target: pool[Math.floor(spotRandom() * pool.length)] };
}

export function routeFor(activity, from, target) {
  if (!target) return [from];
  const [x, z] = target;
  // Long trips swing through the central aisle at z=4.5 (between desk rows and the counter row).
  if (activity === "coffee" || activity === "meeting") return [from, [0, 4.5], [x, 4.5], target];
  // Bedroom and balcony are reached via the west corridor at x=-12.7.
  if (activity === "bedroom" || activity === "balcony") return [from, [0, 4.5], [-12.7, 4.5], target];
  // Flag, bakso and game-room spots hug the outer lanes (x=-13 / x=-5.5).
  if (activity === "flag" || activity === "bakso" || activity === "pingpong" || activity === "arcade") return [from, [x, 4.5], target];
  // Short hops (lounge, water, lesehan, bookshelf, stroll) go straight in.
  return [from, target];
}
