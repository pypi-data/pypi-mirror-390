# Comprehensive Load Testing Methodology

## **Objective**: Identify Software Bottlenecks vs Hardware Limits

The goal is to determine whether concurrency limits are due to **software bottlenecks** (fixable) or **hardware saturation** (requires scaling).

## **Test Design Principles**

### **1. Controlled Escalation**
- Incremental client increases to isolate failure points
- Maintain same workload per client (6 channels)
- Stop at first sign of degradation to analyze root cause

### **2. Multi-Dimensional Monitoring**
- **Performance metrics**: Latency, throughput, error rates
- **Resource utilization**: CPU per core, memory, network, file descriptors
- **Software bottlenecks**: Lock contention, queue depths, threading patterns

### **3. Failure Mode Classification**
- **Hardware saturation**: CPU/memory/network limits reached
- **Software bottlenecks**: Concurrency limits while hardware idle
- **Configuration limits**: OS/application parameter constraints

## **Load Testing Protocol**

### **Phase 1: Baseline Verification (60 clients)**
**Objective**: Confirm current performance as baseline

**Test Steps**:
1. Start with 60 clients, 6 channels each
2. Run for 10 minutes to reach steady state
3. Capture baseline metrics

**Key Metrics**:
- CPU utilization per core (should be ~30% on core 0, ~0% on cores 1-3)
- Memory usage (RSS, heap)
- Response latency (p50, p95, p99)
- Error rate (should be 0%)

### **Phase 2: Incremental Scaling Test**
**Objective**: Find the failure point through controlled escalation

**Test Sequence**:
```
60 → 80 → 100 → 120 → 150 → 180 → 200 → 240+ clients
```

**Per Test Point Protocol**:
1. **Ramp up**: Add 20 clients over 2 minutes (avoid thundering herd)
2. **Steady state**: Run for 10 minutes at target level
3. **Monitor**: Capture all metrics during steady state
4. **Stop condition**: Any degradation triggers analysis before continuing

### **Phase 3: Deep Dive Analysis at Failure Point**
**Objective**: Classify failure mode and identify root cause

**Analysis Protocol**:
1. **Profile at failure point**: Generate flamegraph during degraded performance
2. **Compare to baseline**: Identify what changed in the flamegraph patterns
3. **Resource analysis**: Which resource hit limits first?

## **Monitoring Configuration**

### **System-Level Metrics (Required)**

```bash
# CPU utilization per core
top -p $SERVER_PID -H -d 1

# Memory detailed breakdown
cat /proc/$SERVER_PID/status | grep -E "(VmRSS|VmData|VmStk|VmExe|VmLib)"

# Network connections and sockets
ss -tuln | grep :8080
netstat -an | grep :8080 | wc -l

# File descriptors
ls -la /proc/$SERVER_PID/fd | wc -l
cat /proc/$SERVER_PID/limits | grep "Max open files"
```

### **Application-Level Metrics (Critical)**

**Performance Metrics**:
- **Latency**: Time from client request to first data received
- **Throughput**: Messages/second delivered per client
- **Error rates**: Connection failures, timeouts, exceptions

**Resource Metrics**:
- **Python GIL contention**: If available through profiling
- **Arrow operations per second**: From internal metrics
- **Kafka consumer lag**: If exposed

### **System Resource Limits to Check**

**OS Limits**:
```bash
# Connection limits
ulimit -n  # File descriptors
cat /proc/sys/net/core/somaxconn  # Socket backlog
sysctl net.ipv4.tcp_max_syn_backlog

# Memory limits
cat /proc/sys/vm/max_map_count  # Memory mapping limit
free -h  # Available memory
```

**Application Limits**:
- gRPC connection limits
- PyArrow internal threading limits
- Kafka consumer group limits

## **Expected Failure Modes & Diagnostics**

### **Mode 1: Hardware Saturation (Ideal)**
**Symptoms**:
- CPU reaches 100% on one or more cores
- OR memory usage approaches system limits
- Performance degrades proportionally

**Diagnosis**: **This is good!** - Hardware fully utilized
**Next Step**: Multi-core optimization or horizontal scaling

### **Mode 2: Software Bottleneck (Target for Optimization)**
**Symptoms**:
- Performance degrades while CPU < 80%
- Error rates increase
- Latency spikes

**Potential Root Causes**:
1. **Threading limits**: gRPC connection pool, PyArrow thread limits
2. **Lock contention**: Critical sections not scaling
3. **Memory fragmentation**: Despite global pool
4. **Network bottlenecks**: Socket limits, buffer exhaustion
5. **GIL contention**: Python code not releasing GIL properly

### **Mode 3: Configuration Limits (Easy Fix)**
**Symptoms**:
- Hard failure at specific client count
- "Too many open files" or similar errors

**Common Limits**:
- OS file descriptor limits
- Network connection limits
- Application connection pool limits

## **Test Execution Strategy**

### **Testing Environment Setup**
```bash
# Increase OS limits for testing
ulimit -n 65536  # File descriptors
echo 65536 > /proc/sys/net/core/somaxconn  # Connection backlog

# Enable detailed monitoring
export PYTHONFAULTHANDLER=1  # Python crash debugging
export MALLOC_CHECK_=1       # Memory debugging
```

### **Client Simulation**
- **Same machine vs separate**: Start with same machine to eliminate network variables
- **Gradual connection**: Avoid connection storms that mask real bottlenecks
- **Realistic workload**: Maintain 6 channels per client throughout

### **Profiling Strategy**
```bash
# Capture profile at each major milestone
py-spy record --native --rate 20 -o profile_${CLIENT_COUNT}_clients.svg --pid $SERVER_PID --duration 60

# Monitor at failure point
py-spy record --native --rate 50 -o profile_failure_point.svg --pid $SERVER_PID --duration 120
```

## **Success Criteria & Next Steps**

### **Scenario A: Hardware Saturation at 180+ clients**
- **Result**: 3x capacity increase achieved
- **Next Step**: PyArrow multi-threading optimization
- **Timeline**: Continue vertical scaling

### **Scenario B: Software bottleneck at 80-120 clients**
- **Result**: Specific optimization target identified
- **Next Step**: Address identified bottleneck (threading, memory, locks)
- **Timeline**: 1-2 week optimization cycle

### **Scenario C: Hard limit at predictable point**
- **Result**: Configuration limit hit
- **Next Step**: Adjust limits, repeat test
- **Timeline**: Same day resolution

## **System Context**

### **Current Baseline (60 clients)**
- **CPU Utilization**: 30% of one core, 3 cores idle
- **Performance Profile**: 
  - Kafka operations: ~33-36% (I/O waiting)
  - Threading overhead: ~28-30% (pthread_cond_timedwait)
  - IPC operations: ~33% (Arrow operations)
  - Compute operations: ~17% (well optimized)
  - NumPy conversion: ~8-9%

### **Hardware Configuration**
- **CPU**: 4 physical cores
- **Current utilization**: 7.5% total system utilization (30% of 1 core)
- **Threading model**: Single Python process, multithreaded with GIL-releasing operations

### **Expected Scaling Potential**
- **Conservative**: 200 clients (linear scaling to 100% of one core)
- **Optimistic**: 300-400 clients (with multi-core utilization)
- **Target**: Identify actual limit and optimization opportunities

## **Implementation Notes**

### **Critical Success Factors**
1. **Stop at first degradation** - Don't push past failure to avoid masking root cause
2. **Profile at failure point** - Capture flamegraph when performance degrades
3. **Monitor all resources** - CPU, memory, network, file descriptors
4. **Incremental testing** - 20-client increases to isolate failure points

### **Key Questions to Answer**
1. Does CPU saturate before hitting client limits?
2. What changes in the flamegraph at failure point?
3. Are 3 idle cores utilizable with configuration changes?
4. Is threading overhead (pthread_cond_timedwait) the true ceiling?

---
*Load testing methodology for Arrakis server scaling beyond 60 concurrent clients*
