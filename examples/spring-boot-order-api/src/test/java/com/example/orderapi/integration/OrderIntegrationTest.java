package com.example.orderapi.integration;

import com.example.orderapi.dto.request.CreateOrderRequest;
import com.example.orderapi.entity.Order;
import com.example.orderapi.entity.Product;
import com.example.orderapi.entity.User;
import com.example.orderapi.repository.OrderRepository;
import com.example.orderapi.repository.ProductRepository;
import com.example.orderapi.repository.UserRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureWebMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureWebMvc
@ActiveProfiles("test")
@Transactional
class OrderIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    private User testUser;
    private Product testProduct;

    @BeforeEach
    void setUp() {
        // Create test user
        testUser = new User();
        testUser.setUsername("testuser");
        testUser.setEmail("test@example.com");
        testUser.setPassword(passwordEncoder.encode("password"));
        testUser.setFirstName("Test");
        testUser.setLastName("User");
        testUser.setRole(User.Role.USER);
        testUser.setEnabled(true);
        testUser = userRepository.save(testUser);

        // Create test product
        testProduct = new Product();
        testProduct.setName("Test Product");
        testProduct.setDescription("Test Description");
        testProduct.setPrice(new BigDecimal("99.99"));
        testProduct.setStockQuantity(100);
        testProduct.setCategory("Test Category");
        testProduct.setBrand("Test Brand");
        testProduct.setActive(true);
        testProduct = productRepository.save(testProduct);
    }

    @Test
    @WithMockUser(username = "testuser", roles = "USER")
    void createOrder_ValidRequest_CreatesOrder() throws Exception {
        // Given
        CreateOrderRequest request = new CreateOrderRequest();
        request.setShippingAddress("123 Test Street, Test City");
        
        CreateOrderRequest.OrderItemRequest itemRequest = new CreateOrderRequest.OrderItemRequest();
        itemRequest.setProductId(testProduct.getId());
        itemRequest.setQuantity(2);
        
        request.setItems(List.of(itemRequest));

        // When & Then
        mockMvc.perform(post("/api/orders")
                .with(csrf())
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.status").value("PENDING"))
                .andExpect(jsonPath("$.totalAmount").value(199.98))
                .andExpect(jsonPath("$.shippingAddress").value("123 Test Street, Test City"))
                .andExpect(jsonPath("$.items").isArray())
                .andExpect(jsonPath("$.items[0].quantity").value(2));

        // Verify order was created in database
        List<Order> orders = orderRepository.findByUser(testUser);
        assertEquals(1, orders.size());
        assertEquals(Order.OrderStatus.PENDING, orders.get(0).getStatus());

        // Verify stock was reduced
        Product updatedProduct = productRepository.findById(testProduct.getId()).orElseThrow();
        assertEquals(98, updatedProduct.getStockQuantity());
    }

    @Test
    @WithMockUser(username = "testuser", roles = "USER")
    void createOrder_InsufficientStock_ReturnsBadRequest() throws Exception {
        // Given
        CreateOrderRequest request = new CreateOrderRequest();
        request.setShippingAddress("123 Test Street, Test City");
        
        CreateOrderRequest.OrderItemRequest itemRequest = new CreateOrderRequest.OrderItemRequest();
        itemRequest.setProductId(testProduct.getId());
        itemRequest.setQuantity(200); // More than available stock
        
        request.setItems(List.of(itemRequest));

        // When & Then
        mockMvc.perform(post("/api/orders")
                .with(csrf())
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest());

        // Verify no order was created
        List<Order> orders = orderRepository.findByUser(testUser);
        assertEquals(0, orders.size());

        // Verify stock was not changed
        Product unchangedProduct = productRepository.findById(testProduct.getId()).orElseThrow();
        assertEquals(100, unchangedProduct.getStockQuantity());
    }

    @Test
    @WithMockUser(username = "testuser", roles = "USER")
    void getUserOrders_ReturnsUserOrders() throws Exception {
        // Given - Create an order first
        Order order = new Order();
        order.setUser(testUser);
        order.setTotalAmount(new BigDecimal("99.99"));
        order.setShippingAddress("123 Test Street");
        order.setStatus(Order.OrderStatus.PENDING);
        orderRepository.save(order);

        // When & Then
        mockMvc.perform(get("/api/orders")
                .with(csrf()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content").isArray())
                .andExpect(jsonPath("$.content[0].status").value("PENDING"))
                .andExpect(jsonPath("$.content[0].totalAmount").value(99.99));
    }

    @Test
    @WithMockUser(username = "admin", roles = "ADMIN")
    void confirmOrder_AdminUser_ConfirmsOrder() throws Exception {
        // Given - Create a pending order
        Order order = new Order();
        order.setUser(testUser);
        order.setTotalAmount(new BigDecimal("99.99"));
        order.setShippingAddress("123 Test Street");
        order.setStatus(Order.OrderStatus.PENDING);
        order = orderRepository.save(order);

        // When & Then
        mockMvc.perform(put("/api/orders/{id}/confirm", order.getId())
                .with(csrf()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("CONFIRMED"));

        // Verify order status was updated
        Order updatedOrder = orderRepository.findById(order.getId()).orElseThrow();
        assertEquals(Order.OrderStatus.CONFIRMED, updatedOrder.getStatus());
    }

    @Test
    @WithMockUser(username = "testuser", roles = "USER")
    void confirmOrder_RegularUser_ReturnsForbidden() throws Exception {
        // Given - Create a pending order
        Order order = new Order();
        order.setUser(testUser);
        order.setTotalAmount(new BigDecimal("99.99"));
        order.setShippingAddress("123 Test Street");
        order.setStatus(Order.OrderStatus.PENDING);
        order = orderRepository.save(order);

        // When & Then
        mockMvc.perform(put("/api/orders/{id}/confirm", order.getId())
                .with(csrf()))
                .andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(username = "testuser", roles = "USER")
    void cancelOrder_OwnOrder_CancelsOrder() throws Exception {
        // Given - Create a pending order
        Order order = new Order();
        order.setUser(testUser);
        order.setTotalAmount(new BigDecimal("99.99"));
        order.setShippingAddress("123 Test Street");
        order.setStatus(Order.OrderStatus.PENDING);
        order = orderRepository.save(order);

        // When & Then
        mockMvc.perform(put("/api/orders/{id}/cancel", order.getId())
                .with(csrf()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("CANCELLED"));

        // Verify order status was updated
        Order updatedOrder = orderRepository.findById(order.getId()).orElseThrow();
        assertEquals(Order.OrderStatus.CANCELLED, updatedOrder.getStatus());
    }
}
