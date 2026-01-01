import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/datasources/auth_local_datasource.dart';
import '../../data/datasources/auth_remote_datasource.dart';
import '../../data/models/auth_models.dart';

// Auth state
class AuthState {
  final bool isAuthenticated;
  final bool isLoading;
  final UserModel? user;
  final String? error;

  const AuthState({
    this.isAuthenticated = false,
    this.isLoading = false,
    this.user,
    this.error,
  });

  AuthState copyWith({
    bool? isAuthenticated,
    bool? isLoading,
    UserModel? user,
    String? error,
  }) {
    return AuthState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      isLoading: isLoading ?? this.isLoading,
      user: user ?? this.user,
      error: error,
    );
  }
}

// Auth state notifier
class AuthNotifier extends StateNotifier<AuthState> {
  final AuthLocalDataSource _localStorage;
  final AuthRemoteDataSource _remoteDataSource;

  AuthNotifier(this._localStorage, this._remoteDataSource) 
      : super(const AuthState()) {
    _checkAuthStatus();
  }

  Future<void> _checkAuthStatus() async {
    state = state.copyWith(isLoading: true);
    
    try {
      final hasTokens = await _localStorage.hasValidTokens();
      if (hasTokens) {
        final userJson = await _localStorage.getUser();
        if (userJson != null) {
          final user = UserModel.fromJson(jsonDecode(userJson));
          state = state.copyWith(
            isAuthenticated: true,
            user: user,
            isLoading: false,
          );
          return;
        }
      }
    } catch (e) {
      // Token invalid or expired
    }
    
    state = state.copyWith(isAuthenticated: false, isLoading: false);
  }

  Future<void> register({
    required String email,
    required String password,
    required String name,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final response = await _remoteDataSource.register(
        email: email,
        password: password,
        name: name,
      );
      
      await _saveAuthData(response);
      
      state = state.copyWith(
        isAuthenticated: true,
        user: response.user,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: _parseError(e),
      );
      rethrow;
    }
  }

  Future<void> login({
    required String email,
    required String password,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final response = await _remoteDataSource.login(
        email: email,
        password: password,
      );
      
      await _saveAuthData(response);
      
      state = state.copyWith(
        isAuthenticated: true,
        user: response.user,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: _parseError(e),
      );
      rethrow;
    }
  }

  Future<void> logout() async {
    try {
      await _remoteDataSource.logout();
    } catch (e) {
      // Ignore logout errors
    }
    
    await _localStorage.clearAll();
    state = const AuthState();
  }

  Future<void> _saveAuthData(AuthResponse response) async {
    await _localStorage.saveTokens(
      response.tokens.accessToken,
      response.tokens.refreshToken,
    );
    await _localStorage.saveUser(jsonEncode(response.user.toJson()));
  }

  String _parseError(dynamic error) {
    if (error.toString().contains('401')) {
      return 'Invalid credentials';
    }
    if (error.toString().contains('409')) {
      return 'Email already registered';
    }
    return 'An error occurred. Please try again.';
  }
}

// Providers
final authStateProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(
    ref.watch(authLocalDataSourceProvider),
    ref.watch(authRemoteDataSourceProvider),
  );
});
