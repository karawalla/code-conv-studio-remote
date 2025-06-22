package com.example.orderapi.controller;

import com.example.orderapi.dto.request.LoginRequest;
import com.example.orderapi.dto.request.RegisterRequest;
import com.example.orderapi.entity.User;
import com.example.orderapi.security.JwtTokenProvider;
import com.example.orderapi.service.UserService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(AuthController.class)
class AuthControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private AuthenticationManager authenticationManager;

    @MockBean
    private UserService userService;

    @MockBean
    private JwtTokenProvider tokenProvider;

    @Autowired
    private ObjectMapper objectMapper;

    private User testUser;
    private LoginRequest loginRequest;
    private RegisterRequest registerRequest;

    @BeforeEach
    void setUp() {
        testUser = new User();
        testUser.setId(1L);
        testUser.setUsername("testuser");
        testUser.setEmail("test@example.com");
        testUser.setFirstName("Test");
        testUser.setLastName("User");
        testUser.setRole(User.Role.USER);

        loginRequest = new LoginRequest("testuser", "password");
        
        registerRequest = new RegisterRequest();
        registerRequest.setUsername("newuser");
        registerRequest.setEmail("new@example.com");
        registerRequest.setPassword("password123");
        registerRequest.setFirstName("New");
        registerRequest.setLastName("User");
    }

    @Test
    void login_ValidCredentials_ReturnsAuthResponse() throws Exception {
        // Given
        Authentication authentication = new UsernamePasswordAuthenticationToken(testUser, null, testUser.getAuthorities());
        when(authenticationManager.authenticate(any())).thenReturn(authentication);
        when(tokenProvider.generateToken(authentication)).thenReturn("jwt-token");

        // When & Then
        mockMvc.perform(post("/api/auth/login")
                .with(csrf())
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(loginRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.token").value("jwt-token"))
                .andExpect(jsonPath("$.username").value("testuser"))
                .andExpect(jsonPath("$.email").value("test@example.com"));
    }

    @Test
    void login_InvalidCredentials_ReturnsBadRequest() throws Exception {
        // Given
        LoginRequest invalidRequest = new LoginRequest("", "");

        // When & Then
        mockMvc.perform(post("/api/auth/login")
                .with(csrf())
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(invalidRequest)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void register_ValidData_ReturnsAuthResponse() throws Exception {
        // Given
        when(userService.createUser(anyString(), anyString(), anyString(), anyString(), anyString()))
                .thenReturn(testUser);
        when(tokenProvider.generateTokenFromUsername(anyString())).thenReturn("jwt-token");

        // When & Then
        mockMvc.perform(post("/api/auth/register")
                .with(csrf())
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(registerRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.token").value("jwt-token"))
                .andExpect(jsonPath("$.username").value("testuser"));
    }

    @Test
    void register_InvalidData_ReturnsBadRequest() throws Exception {
        // Given
        RegisterRequest invalidRequest = new RegisterRequest();
        invalidRequest.setUsername(""); // Invalid - empty username

        // When & Then
        mockMvc.perform(post("/api/auth/register")
                .with(csrf())
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(invalidRequest)))
                .andExpect(status().isBadRequest());
    }

    @Test
    @WithMockUser(username = "testuser")
    void refreshToken_AuthenticatedUser_ReturnsNewToken() throws Exception {
        // Given
        when(tokenProvider.generateTokenFromUsername("testuser")).thenReturn("new-jwt-token");

        // When & Then
        mockMvc.perform(post("/api/auth/refresh")
                .with(csrf())
                .principal(() -> "testuser"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.token").value("new-jwt-token"));
    }
}
