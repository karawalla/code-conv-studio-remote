package com.example.orderapi.service;

import com.example.orderapi.entity.Product;
import com.example.orderapi.exception.ResourceNotFoundException;
import com.example.orderapi.repository.ProductRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

@Service
@Transactional
public class ProductService {

    private static final Logger logger = LoggerFactory.getLogger(ProductService.class);

    @Autowired
    private ProductRepository productRepository;

    @Transactional(readOnly = true)
    @Cacheable(value = "products", key = "#id")
    public Product findById(Long id) {
        return productRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Product not found with id: " + id));
    }

    @Transactional(readOnly = true)
    @Cacheable(value = "availableProducts")
    public List<Product> findAvailableProducts() {
        return productRepository.findAvailableProducts();
    }

    @Transactional(readOnly = true)
    public Page<Product> findActiveProducts(Pageable pageable) {
        return productRepository.findByActiveTrue(pageable);
    }

    @Transactional(readOnly = true)
    @Cacheable(value = "productCategories")
    public List<String> findAllCategories() {
        return productRepository.findAllCategories();
    }

    @Transactional(readOnly = true)
    public List<String> findAllBrands() {
        return productRepository.findAllBrands();
    }

    @Transactional(readOnly = true)
    public Page<Product> findByCategory(String category, Pageable pageable) {
        return productRepository.findByCategoryAndActiveTrue(category, pageable);
    }

    @Transactional(readOnly = true)
    public List<Product> findByBrand(String brand) {
        return productRepository.findByBrand(brand);
    }

    @Transactional(readOnly = true)
    public List<Product> findByPriceRange(BigDecimal minPrice, BigDecimal maxPrice) {
        return productRepository.findByPriceRange(minPrice, maxPrice);
    }

    @Transactional(readOnly = true)
    public List<Product> searchProducts(String keyword) {
        return productRepository.searchByKeyword(keyword);
    }

    @Transactional(readOnly = true)
    public List<Product> findLowStockProducts(Integer threshold) {
        return productRepository.findLowStockProducts(threshold);
    }

    @CacheEvict(value = {"products", "availableProducts", "productCategories"}, allEntries = true)
    public Product createProduct(Product product) {
        logger.info("Creating new product: {}", product.getName());
        product.setActive(true);
        Product savedProduct = productRepository.save(product);
        logger.info("Product created successfully: {}", savedProduct.getName());
        return savedProduct;
    }

    @CacheEvict(value = {"products", "availableProducts", "productCategories"}, allEntries = true)
    public Product updateProduct(Long id, Product productDetails) {
        logger.info("Updating product with id: {}", id);
        Product product = findById(id);
        
        product.setName(productDetails.getName());
        product.setDescription(productDetails.getDescription());
        product.setPrice(productDetails.getPrice());
        product.setStockQuantity(productDetails.getStockQuantity());
        product.setCategory(productDetails.getCategory());
        product.setBrand(productDetails.getBrand());
        product.setImageUrl(productDetails.getImageUrl());
        product.setActive(productDetails.isActive());
        
        Product updatedProduct = productRepository.save(product);
        logger.info("Product updated successfully: {}", updatedProduct.getName());
        return updatedProduct;
    }

    @CacheEvict(value = {"products", "availableProducts", "productCategories"}, allEntries = true)
    public void deleteProduct(Long id) {
        logger.info("Deleting product with id: {}", id);
        Product product = findById(id);
        productRepository.delete(product);
        logger.info("Product deleted successfully");
    }

    @CacheEvict(value = {"products", "availableProducts"}, key = "#id")
    public Product updateStock(Long id, Integer quantity) {
        logger.info("Updating stock for product id: {} to quantity: {}", id, quantity);
        Product product = findById(id);
        product.setStockQuantity(quantity);
        return productRepository.save(product);
    }

    @CacheEvict(value = {"products", "availableProducts"}, key = "#id")
    public Product reduceStock(Long id, Integer quantity) {
        logger.info("Reducing stock for product id: {} by quantity: {}", id, quantity);
        Product product = findById(id);
        
        if (product.getStockQuantity() < quantity) {
            throw new IllegalArgumentException("Insufficient stock. Available: " + product.getStockQuantity() + ", Requested: " + quantity);
        }
        
        product.setStockQuantity(product.getStockQuantity() - quantity);
        return productRepository.save(product);
    }

    @CacheEvict(value = {"products", "availableProducts"}, key = "#id")
    public Product increaseStock(Long id, Integer quantity) {
        logger.info("Increasing stock for product id: {} by quantity: {}", id, quantity);
        Product product = findById(id);
        product.setStockQuantity(product.getStockQuantity() + quantity);
        return productRepository.save(product);
    }

    @CacheEvict(value = {"products", "availableProducts", "productCategories"}, key = "#id")
    public Product deactivateProduct(Long id) {
        logger.info("Deactivating product with id: {}", id);
        Product product = findById(id);
        product.setActive(false);
        return productRepository.save(product);
    }

    @CacheEvict(value = {"products", "availableProducts", "productCategories"}, key = "#id")
    public Product activateProduct(Long id) {
        logger.info("Activating product with id: {}", id);
        Product product = findById(id);
        product.setActive(true);
        return productRepository.save(product);
    }
}
