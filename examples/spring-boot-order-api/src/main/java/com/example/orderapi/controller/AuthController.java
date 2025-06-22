package com.example.orderapi.controller;

import com.example.orderapi.dto.request.LoginRequest;
import com.example.orderapi.dto.request.RegisterRequest;
import com.example.orderapi.dto.response.AuthResponse;
import com.example.orderapi.entity.User;
import com.example.orderapi.security.JwtTokenProvider;
import com.example.orderapi.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@Tag(name = "Authentication", description = "Authentication management APIs")
public class AuthController {

    private static final Logger logger = LoggerFactory.getLogger(AuthController.class);

    @Autowired
    private AuthenticationManager authenticationManager;

    @Autowired
    private UserService userService;

    @Autowired
    private JwtTokenProvider tokenProvider;

    @PostMapping("/login")
    @Operation(summary = "User login", description = "Authenticate user and return JWT token")
    public ResponseEntity<AuthResponse> login(@Valid @RequestBody LoginRequest loginRequest) {
        logger.info("Login attempt for user: {}", loginRequest.getUsername());

        Authentication authentication = authenticationManager.authenticate(
            new UsernamePasswordAuthenticationToken(
                loginRequest.getUsername(),
                loginRequest.getPassword()
            )
        );

        SecurityContextHolder.getContext().setAuthentication(authentication);
        String jwt = tokenProvider.generateToken(authentication);

        User user = (User) authentication.getPrincipal();
        
        AuthResponse response = new AuthResponse(
            jwt,
            user.getId(),
            user.getUsername(),
            user.getEmail(),
            user.getFirstName(),
            user.getLastName(),
            user.getRole().toString()
        );

        logger.info("User {} logged in successfully", user.getUsername());
        return ResponseEntity.ok(response);
    }

    @PostMapping("/register")
    @Operation(summary = "User registration", description = "Register a new user account")
    public ResponseEntity<AuthResponse> register(@Valid @RequestBody RegisterRequest registerRequest) {
        logger.info("Registration attempt for user: {}", registerRequest.getUsername());

        User user = userService.createUser(
            registerRequest.getUsername(),
            registerRequest.getEmail(),
            registerRequest.getPassword(),
            registerRequest.getFirstName(),
            registerRequest.getLastName()
        );

        String jwt = tokenProvider.generateTokenFromUsername(user.getUsername());

        AuthResponse response = new AuthResponse(
            jwt,
            user.getId(),
            user.getUsername(),
            user.getEmail(),
            user.getFirstName(),
            user.getLastName(),
            user.getRole().toString()
        );

        logger.info("User {} registered successfully", user.getUsername());
        return ResponseEntity.ok(response);
    }

    @PostMapping("/refresh")
    @Operation(summary = "Refresh token", description = "Refresh JWT token for authenticated user")
    public ResponseEntity<AuthResponse> refreshToken(Authentication authentication) {
        logger.info("Token refresh for user: {}", authentication.getName());

        User user = (User) authentication.getPrincipal();
        String jwt = tokenProvider.generateTokenFromUsername(user.getUsername());

        AuthResponse response = new AuthResponse(
            jwt,
            user.getId(),
            user.getUsername(),
            user.getEmail(),
            user.getFirstName(),
            user.getLastName(),
            user.getRole().toString()
        );

        return ResponseEntity.ok(response);
    }
}
