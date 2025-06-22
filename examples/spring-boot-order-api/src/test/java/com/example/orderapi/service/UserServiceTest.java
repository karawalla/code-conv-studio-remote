package com.example.orderapi.service;

import com.example.orderapi.entity.User;
import com.example.orderapi.exception.ResourceNotFoundException;
import com.example.orderapi.exception.UserAlreadyExistsException;
import com.example.orderapi.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @InjectMocks
    private UserService userService;

    private User testUser;

    @BeforeEach
    void setUp() {
        testUser = new User();
        testUser.setId(1L);
        testUser.setUsername("testuser");
        testUser.setEmail("test@example.com");
        testUser.setPassword("encodedPassword");
        testUser.setFirstName("Test");
        testUser.setLastName("User");
        testUser.setRole(User.Role.USER);
        testUser.setEnabled(true);
    }

    @Test
    void loadUserByUsername_ExistingUser_ReturnsUser() {
        // Given
        when(userRepository.findByUsername("testuser")).thenReturn(Optional.of(testUser));

        // When
        User result = (User) userService.loadUserByUsername("testuser");

        // Then
        assertNotNull(result);
        assertEquals("testuser", result.getUsername());
        verify(userRepository).findByUsername("testuser");
    }

    @Test
    void loadUserByUsername_NonExistingUser_ThrowsException() {
        // Given
        when(userRepository.findByUsername("nonexistent")).thenReturn(Optional.empty());

        // When & Then
        assertThrows(UsernameNotFoundException.class, 
            () -> userService.loadUserByUsername("nonexistent"));
        verify(userRepository).findByUsername("nonexistent");
    }

    @Test
    void findById_ExistingUser_ReturnsUser() {
        // Given
        when(userRepository.findById(1L)).thenReturn(Optional.of(testUser));

        // When
        User result = userService.findById(1L);

        // Then
        assertNotNull(result);
        assertEquals(1L, result.getId());
        verify(userRepository).findById(1L);
    }

    @Test
    void findById_NonExistingUser_ThrowsException() {
        // Given
        when(userRepository.findById(999L)).thenReturn(Optional.empty());

        // When & Then
        assertThrows(ResourceNotFoundException.class, 
            () -> userService.findById(999L));
        verify(userRepository).findById(999L);
    }

    @Test
    void createUser_ValidData_ReturnsCreatedUser() {
        // Given
        when(userRepository.existsByUsername("newuser")).thenReturn(false);
        when(userRepository.existsByEmail("new@example.com")).thenReturn(false);
        when(passwordEncoder.encode("password")).thenReturn("encodedPassword");
        when(userRepository.save(any(User.class))).thenReturn(testUser);

        // When
        User result = userService.createUser("newuser", "new@example.com", "password", "New", "User");

        // Then
        assertNotNull(result);
        verify(userRepository).existsByUsername("newuser");
        verify(userRepository).existsByEmail("new@example.com");
        verify(passwordEncoder).encode("password");
        verify(userRepository).save(any(User.class));
    }

    @Test
    void createUser_ExistingUsername_ThrowsException() {
        // Given
        when(userRepository.existsByUsername("existinguser")).thenReturn(true);

        // When & Then
        assertThrows(UserAlreadyExistsException.class, 
            () -> userService.createUser("existinguser", "new@example.com", "password", "New", "User"));
        verify(userRepository).existsByUsername("existinguser");
        verify(userRepository, never()).save(any(User.class));
    }

    @Test
    void createUser_ExistingEmail_ThrowsException() {
        // Given
        when(userRepository.existsByUsername("newuser")).thenReturn(false);
        when(userRepository.existsByEmail("existing@example.com")).thenReturn(true);

        // When & Then
        assertThrows(UserAlreadyExistsException.class, 
            () -> userService.createUser("newuser", "existing@example.com", "password", "New", "User"));
        verify(userRepository).existsByUsername("newuser");
        verify(userRepository).existsByEmail("existing@example.com");
        verify(userRepository, never()).save(any(User.class));
    }

    @Test
    void changePassword_ValidOldPassword_UpdatesPassword() {
        // Given
        when(userRepository.findById(1L)).thenReturn(Optional.of(testUser));
        when(passwordEncoder.matches("oldPassword", "encodedPassword")).thenReturn(true);
        when(passwordEncoder.encode("newPassword")).thenReturn("newEncodedPassword");
        when(userRepository.save(any(User.class))).thenReturn(testUser);

        // When
        User result = userService.changePassword(1L, "oldPassword", "newPassword");

        // Then
        assertNotNull(result);
        verify(passwordEncoder).matches("oldPassword", "encodedPassword");
        verify(passwordEncoder).encode("newPassword");
        verify(userRepository).save(any(User.class));
    }

    @Test
    void changePassword_InvalidOldPassword_ThrowsException() {
        // Given
        when(userRepository.findById(1L)).thenReturn(Optional.of(testUser));
        when(passwordEncoder.matches("wrongPassword", "encodedPassword")).thenReturn(false);

        // When & Then
        assertThrows(IllegalArgumentException.class, 
            () -> userService.changePassword(1L, "wrongPassword", "newPassword"));
        verify(passwordEncoder).matches("wrongPassword", "encodedPassword");
        verify(userRepository, never()).save(any(User.class));
    }

    @Test
    void promoteToAdmin_ExistingUser_UpdatesRole() {
        // Given
        when(userRepository.findById(1L)).thenReturn(Optional.of(testUser));
        when(userRepository.save(any(User.class))).thenReturn(testUser);

        // When
        User result = userService.promoteToAdmin(1L);

        // Then
        assertNotNull(result);
        assertEquals(User.Role.ADMIN, testUser.getRole());
        verify(userRepository).findById(1L);
        verify(userRepository).save(testUser);
    }
}
