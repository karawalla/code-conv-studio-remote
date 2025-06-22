package com.example.orderapi.controller;

import com.example.orderapi.entity.Product;
import com.example.orderapi.service.ProductService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;

@RestController
@RequestMapping("/api/products")
@Tag(name = "Products", description = "Product management APIs")
public class ProductController {

    private static final Logger logger = LoggerFactory.getLogger(ProductController.class);

    @Autowired
    private ProductService productService;

    @GetMapping
    @Operation(summary = "Get all products", description = "Retrieve paginated list of active products")
    public ResponseEntity<Page<Product>> getAllProducts(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "name") String sortBy,
            @RequestParam(defaultValue = "asc") String sortDir) {
        
        Sort sort = sortDir.equalsIgnoreCase("desc") ? 
            Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        
        Pageable pageable = PageRequest.of(page, size, sort);
        Page<Product> products = productService.findActiveProducts(pageable);
        
        return ResponseEntity.ok(products);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get product by ID", description = "Retrieve a specific product by its ID")
    public ResponseEntity<Product> getProductById(@PathVariable Long id) {
        logger.info("Fetching product with id: {}", id);
        Product product = productService.findById(id);
        return ResponseEntity.ok(product);
    }

    @GetMapping("/available")
    @Operation(summary = "Get available products", description = "Retrieve all products that are active and in stock")
    public ResponseEntity<List<Product>> getAvailableProducts() {
        List<Product> products = productService.findAvailableProducts();
        return ResponseEntity.ok(products);
    }

    @GetMapping("/categories")
    @Operation(summary = "Get all categories", description = "Retrieve list of all product categories")
    public ResponseEntity<List<String>> getAllCategories() {
        List<String> categories = productService.findAllCategories();
        return ResponseEntity.ok(categories);
    }

    @GetMapping("/brands")
    @Operation(summary = "Get all brands", description = "Retrieve list of all product brands")
    public ResponseEntity<List<String>> getAllBrands() {
        List<String> brands = productService.findAllBrands();
        return ResponseEntity.ok(brands);
    }

    @GetMapping("/category/{category}")
    @Operation(summary = "Get products by category", description = "Retrieve paginated products by category")
    public ResponseEntity<Page<Product>> getProductsByCategory(
            @PathVariable String category,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        
        Pageable pageable = PageRequest.of(page, size);
        Page<Product> products = productService.findByCategory(category, pageable);
        return ResponseEntity.ok(products);
    }

    @GetMapping("/brand/{brand}")
    @Operation(summary = "Get products by brand", description = "Retrieve products by brand")
    public ResponseEntity<List<Product>> getProductsByBrand(@PathVariable String brand) {
        List<Product> products = productService.findByBrand(brand);
        return ResponseEntity.ok(products);
    }

    @GetMapping("/search")
    @Operation(summary = "Search products", description = "Search products by keyword in name or description")
    public ResponseEntity<List<Product>> searchProducts(@RequestParam String keyword) {
        List<Product> products = productService.searchProducts(keyword);
        return ResponseEntity.ok(products);
    }

    @GetMapping("/price-range")
    @Operation(summary = "Get products by price range", description = "Retrieve products within specified price range")
    public ResponseEntity<List<Product>> getProductsByPriceRange(
            @RequestParam BigDecimal minPrice,
            @RequestParam BigDecimal maxPrice) {
        List<Product> products = productService.findByPriceRange(minPrice, maxPrice);
        return ResponseEntity.ok(products);
    }

    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "Create product", description = "Create a new product (Admin only)")
    public ResponseEntity<Product> createProduct(@Valid @RequestBody Product product) {
        logger.info("Creating new product: {}", product.getName());
        Product createdProduct = productService.createProduct(product);
        return new ResponseEntity<>(createdProduct, HttpStatus.CREATED);
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "Update product", description = "Update an existing product (Admin only)")
    public ResponseEntity<Product> updateProduct(@PathVariable Long id, @Valid @RequestBody Product product) {
        logger.info("Updating product with id: {}", id);
        Product updatedProduct = productService.updateProduct(id, product);
        return ResponseEntity.ok(updatedProduct);
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "Delete product", description = "Delete a product (Admin only)")
    public ResponseEntity<Void> deleteProduct(@PathVariable Long id) {
        logger.info("Deleting product with id: {}", id);
        productService.deleteProduct(id);
        return ResponseEntity.noContent().build();
    }

    @PutMapping("/{id}/stock")
    @PreAuthorize("hasRole('ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "Update product stock", description = "Update product stock quantity (Admin only)")
    public ResponseEntity<Product> updateStock(@PathVariable Long id, @RequestParam Integer quantity) {
        logger.info("Updating stock for product id: {} to quantity: {}", id, quantity);
        Product updatedProduct = productService.updateStock(id, quantity);
        return ResponseEntity.ok(updatedProduct);
    }

    @PutMapping("/{id}/deactivate")
    @PreAuthorize("hasRole('ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "Deactivate product", description = "Deactivate a product (Admin only)")
    public ResponseEntity<Product> deactivateProduct(@PathVariable Long id) {
        logger.info("Deactivating product with id: {}", id);
        Product deactivatedProduct = productService.deactivateProduct(id);
        return ResponseEntity.ok(deactivatedProduct);
    }

    @PutMapping("/{id}/activate")
    @PreAuthorize("hasRole('ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "Activate product", description = "Activate a product (Admin only)")
    public ResponseEntity<Product> activateProduct(@PathVariable Long id) {
        logger.info("Activating product with id: {}", id);
        Product activatedProduct = productService.activateProduct(id);
        return ResponseEntity.ok(activatedProduct);
    }

    @GetMapping("/low-stock")
    @PreAuthorize("hasRole('ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "Get low stock products", description = "Get products with stock below threshold (Admin only)")
    public ResponseEntity<List<Product>> getLowStockProducts(@RequestParam(defaultValue = "10") Integer threshold) {
        List<Product> products = productService.findLowStockProducts(threshold);
        return ResponseEntity.ok(products);
    }
}
