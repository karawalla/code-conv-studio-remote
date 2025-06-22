package com.example.orderapi.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.cache.CacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.cache.RedisCacheConfiguration;
import org.springframework.data.redis.cache.RedisCacheManager;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.StringRedisSerializer;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

@Configuration
public class CacheConfig {

    @Value("${app.cache.product-ttl:3600}")
    private long productTtl;

    @Value("${app.cache.user-ttl:1800}")
    private long userTtl;

    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory connectionFactory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);
        
        // Use String serializer for keys
        template.setKeySerializer(new StringRedisSerializer());
        template.setHashKeySerializer(new StringRedisSerializer());
        
        // Use JSON serializer for values
        template.setValueSerializer(new GenericJackson2JsonRedisSerializer());
        template.setHashValueSerializer(new GenericJackson2JsonRedisSerializer());
        
        template.afterPropertiesSet();
        return template;
    }

    @Bean
    public CacheManager cacheManager(RedisConnectionFactory connectionFactory) {
        RedisCacheConfiguration defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
                .entryTtl(Duration.ofSeconds(600)) // Default 10 minutes
                .serializeKeysWith(org.springframework.data.redis.serializer.RedisSerializationContext.SerializationPair
                        .fromSerializer(new StringRedisSerializer()))
                .serializeValuesWith(org.springframework.data.redis.serializer.RedisSerializationContext.SerializationPair
                        .fromSerializer(new GenericJackson2JsonRedisSerializer()));

        // Configure specific cache TTLs
        Map<String, RedisCacheConfiguration> cacheConfigurations = new HashMap<>();
        
        // Products cache - longer TTL since products don't change frequently
        cacheConfigurations.put("products", defaultConfig.entryTtl(Duration.ofSeconds(productTtl)));
        
        // Product categories cache
        cacheConfigurations.put("productCategories", defaultConfig.entryTtl(Duration.ofSeconds(productTtl)));
        
        // User profile cache - shorter TTL for security
        cacheConfigurations.put("userProfiles", defaultConfig.entryTtl(Duration.ofSeconds(userTtl)));
        
        // Available products cache
        cacheConfigurations.put("availableProducts", defaultConfig.entryTtl(Duration.ofSeconds(300))); // 5 minutes
        
        // Order statistics cache
        cacheConfigurations.put("orderStats", defaultConfig.entryTtl(Duration.ofSeconds(900))); // 15 minutes

        return RedisCacheManager.builder(connectionFactory)
                .cacheDefaults(defaultConfig)
                .withInitialCacheConfigurations(cacheConfigurations)
                .build();
    }
}
