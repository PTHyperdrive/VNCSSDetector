class UserModel {
  final String id;
  final String email;
  final String name;
  final List<WorkspaceRole>? workspaces;

  UserModel({
    required this.id,
    required this.email,
    required this.name,
    this.workspaces,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'],
      email: json['email'],
      name: json['name'],
      workspaces: (json['workspaces'] as List<dynamic>?)
          ?.map((w) => WorkspaceRole.fromJson(w))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'email': email,
    'name': name,
    'workspaces': workspaces?.map((w) => w.toJson()).toList(),
  };
}

class WorkspaceRole {
  final String id;
  final String name;
  final String role;

  WorkspaceRole({
    required this.id,
    required this.name,
    required this.role,
  });

  factory WorkspaceRole.fromJson(Map<String, dynamic> json) {
    return WorkspaceRole(
      id: json['id'],
      name: json['name'],
      role: json['role'],
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'role': role,
  };
}

class TokensResponse {
  final String accessToken;
  final String refreshToken;
  final int expiresIn;

  TokensResponse({
    required this.accessToken,
    required this.refreshToken,
    required this.expiresIn,
  });

  factory TokensResponse.fromJson(Map<String, dynamic> json) {
    return TokensResponse(
      accessToken: json['accessToken'] ?? json['access_token'],
      refreshToken: json['refreshToken'] ?? json['refresh_token'],
      expiresIn: json['expiresIn'] ?? json['expires_in'] ?? 900,
    );
  }
}

class AuthResponse {
  final UserModel user;
  final TokensResponse tokens;

  AuthResponse({
    required this.user,
    required this.tokens,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      user: UserModel.fromJson(json['user']),
      tokens: TokensResponse.fromJson(json['tokens']),
    );
  }
}
