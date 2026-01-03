/**
 * Authentication store
 */
import { writable, derived } from 'svelte/store';
import { api, type User } from '$lib/api';

interface AuthState {
    user: User | null;
    loading: boolean;
    initialized: boolean;
}

function createAuthStore() {
    const { subscribe, set, update } = writable<AuthState>({
        user: null,
        loading: true,
        initialized: false
    });

    return {
        subscribe,

        async initialize() {
            const token = api.getToken();
            if (!token) {
                set({ user: null, loading: false, initialized: true });
                return;
            }

            try {
                const user = await api.getCurrentUser();
                set({ user, loading: false, initialized: true });
            } catch {
                api.setToken(null);
                set({ user: null, loading: false, initialized: true });
            }
        },

        async login(email: string, password: string) {
            update(s => ({ ...s, loading: true }));
            try {
                await api.login(email, password);
                const user = await api.getCurrentUser();
                set({ user, loading: false, initialized: true });
                return { success: true };
            } catch (error) {
                update(s => ({ ...s, loading: false }));
                return {
                    success: false,
                    error: error instanceof Error ? error.message : 'Login failed'
                };
            }
        },

        async logout() {
            await api.logout();
            set({ user: null, loading: false, initialized: true });
        },

        setUser(user: User) {
            update(s => ({ ...s, user }));
        }
    };
}

export const auth = createAuthStore();

export const isAuthenticated = derived(auth, $auth => $auth.user !== null);
export const isAdmin = derived(auth, $auth => $auth.user?.role === 'admin');
export const isOperator = derived(auth, $auth =>
    $auth.user?.role === 'admin' || $auth.user?.role === 'operator'
);
