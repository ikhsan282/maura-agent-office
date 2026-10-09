import test from "node:test";
import assert from "node:assert/strict";
import {
  IDLE_WANDER_INTERVAL,
  activityLabel,
  chooseActivityTarget,
  nextWanderAt,
  routeFor
} from "../public/idle-wandering.mjs";

test("idle wandering waits about 32 seconds between destinations", () => {
  assert.equal(IDLE_WANDER_INTERVAL, 32);
  assert.equal(nextWanderAt(100, "idle", () => 0.5), 132);
  assert.equal(nextWanderAt(100, "working", () => 0.5), Infinity);
});

test("chat agents go to meeting and stay there", () => {
  const target = chooseActivityTarget("chat", () => 0.5, () => 0);
  assert.equal(target.activity, "meeting");
  assert.equal(nextWanderAt(100, "chat"), Infinity);
});

test("target selection exposes expanded spots and labels", () => {
  const target = chooseActivityTarget("idle", () => 0.01, () => 0);
  assert.equal(target.activity, "lounge");
  assert.equal(activityLabel("lounge"), "🛋️ Santai di lounge");
  assert.equal(activityLabel("water"), "🚰 Ambil air galon");
  assert.equal(activityLabel("bookshelf"), "📚 Baca di bookshelf");
});

test("routes use safe aisle waypoints before destination", () => {
  assert.deepEqual(routeFor("coffee", [0, 0], [-6, 7]), [[0, 0], [0, 4.5], [-6, 4.5], [-6, 7]]);
  assert.deepEqual(routeFor("arcade", [0, 0], [8, -5.5]), [[0, 0], [8, 4.5], [8, -5.5]]);
});
