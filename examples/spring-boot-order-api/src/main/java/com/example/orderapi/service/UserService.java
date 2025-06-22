package com.example.orderapi.service;

import com.example.orderapi.entity.User;
import com.example.orderapi.exception.ResourceNotFoundException;
import com.example.orderapi.exception.UserAlreadyExistsException;
import com.example.orderapi.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class UserService implements UserDetailsService {

    private static final Logger logger = LoggerFactory.getLogger(UserService.class);

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Override
    @Transactional(readOnly = true)
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new UsernameNotFoundException("User not found with username: " + username));
        
        logger.debug("User found: {}", username);
        return user;
    }

    @Transactional(readOnly = true)
    @Cacheable(value = "userProfiles", key = "#id")
    public User findById(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + id));
    }

    @Transactional(readOnly = true)
    public Optional<User> findByUsername(String username) {
        return userRepository.findByUsername(username);
    }

    @Transactional(readOnly = true)
    public Optional<User> findByEmail(String email) {
        return userRepository.findByEmail(email);
    }

    public User createUser(String username, String email, String password, String firstName, String lastName) {
        logger.info("Creating new user: {}", username);

        if (userRepository.existsByUsername(username)) {
            throw new UserAlreadyExistsException("Username is already taken: " + username);
        }

        if (userRepository.existsByEmail(email)) {
            throw new UserAlreadyExistsException("Email is already in use: " + email);
        }

        User user = new User(username, email, passwordEncoder.encode(password), firstName, lastName);
        user.setRole(User.Role.USER);
        user.setEnabled(true);

        User savedUser = userRepository.save(user);
        logger.info("User created successfully: {}", savedUser.getUsername());
        
        return savedUser;
    }

    @CacheEvict(value = "userProfiles", key = "#user.id")
    public User updateUser(User user) {
        logger.info("Updating user: {}", user.getUsername());
        return userRepository.save(user);
    }

    @CacheEvict(value = "userProfiles", key = "#id")
    public void deleteUser(Long id) {
        logger.info("Deleting user with id: {}", id);
        User user = findById(id);
        userRepository.delete(user);
    }

    @Transactional(readOnly = true)
    public List<User> findAllUsers() {
        return userRepository.findAll();
    }

    @Transactional(readOnly = true)
    public List<User> findUsersByRole(User.Role role) {
        return userRepository.findByRole(role);
    }

    @Transactional(readOnly = true)
    public List<User> findRecentUsers(int days) {
        LocalDateTime startDate = LocalDateTime.now().minusDays(days);
        return userRepository.findUsersCreatedAfter(startDate);
    }

    @Transactional(readOnly = true)
    public long getUserCountByRole(User.Role role) {
        return userRepository.countByRole(role);
    }

    public User promoteToAdmin(Long userId) {
        logger.info("Promoting user to admin: {}", userId);
        User user = findById(userId);
        user.setRole(User.Role.ADMIN);
        return updateUser(user);
    }

    public User enableUser(Long userId) {
        logger.info("Enabling user: {}", userId);
        User user = findById(userId);
        user.setEnabled(true);
        return updateUser(user);
    }

    public User disableUser(Long userId) {
        logger.info("Disabling user: {}", userId);
        User user = findById(userId);
        user.setEnabled(false);
        return updateUser(user);
    }

    @CacheEvict(value = "userProfiles", key = "#userId")
    public User changePassword(Long userId, String oldPassword, String newPassword) {
        logger.info("Changing password for user: {}", userId);
        User user = findById(userId);
        
        if (!passwordEncoder.matches(oldPassword, user.getPassword())) {
            throw new IllegalArgumentException("Old password is incorrect");
        }
        
        user.setPassword(passwordEncoder.encode(newPassword));
        return updateUser(user);
    }
}
