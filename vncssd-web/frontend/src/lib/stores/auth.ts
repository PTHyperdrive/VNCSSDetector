/**
 * Authentication store - Session cookie based
 * Browser handles cookies automatically, no manual token management
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
            try {
                // Check if we have a valid session
                const result = await api.checkAuth();
                if (result.authenticated && result.user) {
                    set({ user: result.user, loading: false, initialized: true });
                } else {
                    set({ user: null, loading: false, initialized: true });
                }
            } catch {
                set({ user: null, loading: false, initialized: true });
            }
        },

        async login(email: string, password: string) {
            update(s => ({ ...s, loading: true }));
            try {
                const result = await api.login(email, password);
                if (result.success && result.user) {
                    set({ user: result.user, loading: false, initialized: true });
                    return { success: true };
                }
                return { success: false, error: 'Login failed' };
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
