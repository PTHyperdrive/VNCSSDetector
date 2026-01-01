class ApiConstants {
  static const String baseUrl = 'http://localhost:3000/api/v1';
  
  // Auth
  static const String register = '/auth/register';
  static const String login = '/auth/login';
  static const String refresh = '/auth/refresh';
  static const String logout = '/auth/logout';
  
  // Status
  static const String status = '/status';
  
  // Nodes
  static const String nodes = '/nodes';
  static const String nodesTopology = '/nodes/topology';
  static String nodeDetail(String id) => '/nodes/$id';
  static String nodeCommands(String id) => '/nodes/$id/commands';
  
  // Events
  static const String events = '/events';
  
  // Notifications
  static const String deviceTokens = '/device-tokens';
  static const String notifications = '/notifications';
  static String notificationRead(String id) => '/notifications/$id/read';
}

class StorageKeys {
  static const String accessToken = 'access_token';
  static const String refreshToken = 'refresh_token';
  static const String user = 'user';
}
