# Performance Audit & Optimization Plan

## Current Bottlenecks Identified

### 1. **Model Loading (CRITICAL)**
- **Issue**: BFloat16 on CPU is slower than Float32 for inference on older CPUs
- **Impact**: 20-30% slower inference
- **Solution**: Use dynamic precision based on CPU features, default to Float32
- **Priority**: HIGH

### 2. **Tokenization Overhead**
- **Issue**: Tokenizer recreates tensors every request
- **Impact**: 100-200ms per request
- **Solution**: Add tokenizer warmup, enable fast tokenizers
- **Priority**: MEDIUM

### 3. **Generation Parameters Not Optimized for Speed**
- **Issue**: `do_sample=True` with temperature is slower than greedy
- **Impact**: 30-40% slower
- **Solution**: When temperature < 0.3, use greedy; add dynamic batching
- **Priority**: HIGH

### 4. **No Response Caching**
- **Issue**: Same questions generate responses every time
- **Impact**: Wasted computation
- **Solution**: Add LRU cache for recent queries
- **Priority**: MEDIUM

### 5. **Attention Mask Not Optimized**
- **Issue**: Attention computed for padding tokens
- **Impact**: 10-15% overhead
- **Solution**: Use attention masks properly
- **Priority**: LOW

### 6. **No Early Stopping**
- **Issue**: Generates until max_length even if complete
- **Impact**: Unnecessary tokens
- **Solution**: Better stopping criteria, detect sentence completion
- **Priority**: MEDIUM

### 7. **Thread Locking on Generation**
- **Issue**: Flask blocking on generation prevents concurrent requests
- **Impact**: Can't handle multiple users
- **Solution**: Add queue system with threading
- **Priority**: LOW (single user app)

### 8. **Static Allocation**
- **Issue**: Tensors allocated/deallocated each request
- **Impact**: Memory fragmentation
- **Solution**: Pre-allocate tensor buffers
- **Priority**: LOW

## Implementation Priority

### Phase 1 (Immediate - 3-5x speedup)
1. ✅ Fix Float32 vs BFloat16 for CPU
2. ✅ Optimize generation parameters (greedy when temp < 0.3)
3. ✅ Add response caching (LRU)
4. ✅ Better early stopping

### Phase 2 (Near-term - 1.5-2x additional speedup)
5. Enable fast tokenizers
6. Add attention mask optimization
7. Warmup model on startup

### Phase 3 (Future)
8. Threading/queue system
9. Static tensor allocation

## Expected Performance Gains

| Optimization | Expected Speedup | Implementation Difficulty |
|--------------|------------------|---------------------------|
| Float32 on CPU | 1.3-1.5x | Easy |
| Greedy decoding | 1.3-1.5x | Easy |
| Response caching | ∞ (cached) | Easy |
| Early stopping | 1.2-1.3x | Medium |
| Fast tokenizers | 1.1-1.2x | Easy |
| Attention masks | 1.1-1.15x | Medium |
| **Total Combined** | **2.5-4x** | - |
