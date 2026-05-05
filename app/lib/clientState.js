export const STORAGE_KEY = "atlas_learning_state_v2";

export const DEFAULT_STATE = {
  isLoggedIn: true,
  course: {
    progress: 100,
    completed: true,
    completedOn: "April 28, 2026",
    lastLesson: "Theme and color systems",
  },
};

export function getClientState() {
  if (typeof window === "undefined") {
    return DEFAULT_STATE;
  }

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return DEFAULT_STATE;
    }
    const parsed = JSON.parse(raw);
    return {
      ...DEFAULT_STATE,
      ...parsed,
      course: {
        ...DEFAULT_STATE.course,
        ...(parsed.course || {}),
      },
    };
  } catch {
    return DEFAULT_STATE;
  }
}

export function saveClientState(nextState) {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(nextState));
}

export function applyLogin(state) {
  return { ...state, isLoggedIn: true };
}

export function applyLogout(state) {
  return { ...state, isLoggedIn: false };
}

export function applyCourseCompletion(state) {
  return {
    ...state,
    course: {
      ...state.course,
      progress: 100,
      completed: true,
      completedOn: "April 28, 2026",
    },
  };
}
