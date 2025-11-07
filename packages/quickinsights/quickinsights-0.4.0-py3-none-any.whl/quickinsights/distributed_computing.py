"""
QuickInsights - Distributed Computing Support System

This module provides distributed computing capabilities including:
- Distributed processing across multiple nodes
- Load balancing and task distribution
- Cluster management and monitoring
- Fault tolerance and recovery
- Distributed caching and data sharing
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue
import socket
import pickle
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NodeStatus(Enum):
    """Node status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class NodeInfo:
    """Information about a computing node"""
    
    node_id: str
    hostname: str
    ip_address: str
    port: int
    cpu_cores: int
    memory_gb: float
    status: NodeStatus
    current_load: float = 0.0
    last_heartbeat: datetime = field(default_factory=datetime.now)
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DistributedTask:
    """Task to be distributed across nodes"""
    
    task_id: str
    task_type: str
    payload: Any
    priority: TaskPriority
    created_at: datetime
    assigned_node: Optional[str] = None
    status: str = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ClusterMetrics:
    """Cluster performance and health metrics"""
    
    total_nodes: int
    active_nodes: int
    total_cpu_cores: int
    total_memory_gb: float
    average_load: float
    tasks_queued: int
    tasks_running: int
    tasks_completed: int
    tasks_failed: int
    timestamp: datetime

class LoadBalancer:
    """Intelligent load balancing for distributed tasks"""
    
    def __init__(self, strategy: str = "round_robin"):
        self.strategy = strategy
        self.node_assignments: Dict[str, int] = {}
        self.last_assignment_index = 0
    
    def select_node(self, available_nodes: List[NodeInfo], task: DistributedTask) -> Optional[NodeInfo]:
        """Select the best node for a task based on strategy"""
        
        if not available_nodes:
            return None
        
        if self.strategy == "round_robin":
            return self._round_robin_selection(available_nodes)
        elif self.strategy == "least_loaded":
            return self._least_loaded_selection(available_nodes)
        elif self.strategy == "capability_based":
            return self._capability_based_selection(available_nodes, task)
        elif self.strategy == "priority_based":
            return self._priority_based_selection(available_nodes, task)
        else:
            return self._round_robin_selection(available_nodes)
    
    def _round_robin_selection(self, nodes: List[NodeInfo]) -> NodeInfo:
        """Round-robin node selection"""
        if not nodes:
            return None
        
        self.last_assignment_index = (self.last_assignment_index + 1) % len(nodes)
        return nodes[self.last_assignment_index]
    
    def _least_loaded_selection(self, nodes: List[NodeInfo]) -> NodeInfo:
        """Select node with lowest current load"""
        if not nodes:
            return None
        
        return min(nodes, key=lambda n: n.current_load)
    
    def _capability_based_selection(self, nodes: List[NodeInfo], task: DistributedTask) -> NodeInfo:
        """Select node based on task requirements and node capabilities"""
        if not nodes:
            return None
        
        # Filter nodes by capabilities
        capable_nodes = [
            node for node in nodes 
            if task.task_type in node.capabilities
        ]
        
        if not capable_nodes:
            # Fall back to least loaded if no capability match
            return self._least_loaded_selection(nodes)
        
        return self._least_loaded_selection(capable_nodes)
    
    def _priority_based_selection(self, nodes: List[NodeInfo], task: DistributedTask) -> NodeInfo:
        """Select node based on task priority and node performance"""
        if not nodes:
            return None
        
        # For high priority tasks, prefer high-performance nodes
        if task.priority in [TaskPriority.HIGH, TaskPriority.CRITICAL]:
            # Sort by performance (CPU cores + memory)
            sorted_nodes = sorted(
                nodes, 
                key=lambda n: (n.cpu_cores, n.memory_gb), 
                reverse=True
            )
            return sorted_nodes[0]
        else:
            # For normal priority, use least loaded
            return self._least_loaded_selection(nodes)

class TaskQueue:
    """Priority-based task queue for distributed processing"""
    
    def __init__(self):
        self.high_priority_queue = queue.PriorityQueue()
        self.normal_priority_queue = queue.Queue()
        self.low_priority_queue = queue.Queue()
        self.lock = threading.Lock()
    
    def add_task(self, task: DistributedTask) -> bool:
        """Add task to appropriate priority queue"""
        try:
            if task.priority == TaskPriority.CRITICAL:
                self.high_priority_queue.put((-4, time.time(), task))
            elif task.priority == TaskPriority.HIGH:
                self.high_priority_queue.put((-3, time.time(), task))
            elif task.priority == TaskPriority.NORMAL:
                self.normal_priority_queue.put(task)
            else:  # LOW priority
                self.low_priority_queue.put(task)
            return True
        except Exception as e:
            logger.error(f"Failed to add task {task.task_id}: {e}")
            return False
    
    def get_next_task(self) -> Optional[DistributedTask]:
        """Get next task based on priority"""
        try:
            # Check high priority first
            if not self.high_priority_queue.empty():
                _, _, task = self.high_priority_queue.get_nowait()
                return task
            
            # Check normal priority
            if not self.normal_priority_queue.empty():
                return self.normal_priority_queue.get_nowait()
            
            # Check low priority
            if not self.low_priority_queue.empty():
                return self.low_priority_queue.get_nowait()
            
            return None
        except queue.Empty:
            return None
    
    def get_queue_status(self) -> Dict[str, int]:
        """Get current queue status"""
        return {
            "high_priority": self.high_priority_queue.qsize(),
            "normal_priority": self.normal_priority_queue.qsize(),
            "low_priority": self.low_priority_queue.qsize()
        }

class DistributedCache:
    """Distributed caching system with consistency management"""
    
    def __init__(self, consistency_level: str = "eventual"):
        self.consistency_level = consistency_level
        self.cache_data: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, float] = {}
        self.cache_ttl: Dict[str, float] = {}
        self.lock = threading.RLock()
        
        # Cleanup thread for expired entries
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from distributed cache"""
        with self.lock:
            if key not in self.cache_data:
                return None
            
            # Check TTL
            if key in self.cache_ttl:
                if time.time() - self.cache_timestamps[key] > self.cache_ttl[key]:
                    # Expired, remove
                    del self.cache_data[key]
                    del self.cache_timestamps[key]
                    del self.cache_ttl[key]
                    return None
            
            return self.cache_data[key]
    
    def set(self, key: str, value: Any, ttl: float = 3600) -> bool:
        """Set value in distributed cache"""
        try:
            with self.lock:
                self.cache_data[key] = value
                self.cache_timestamps[key] = time.time()
                self.cache_ttl[key] = ttl
            return True
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {e}")
            return False
    
    def invalidate(self, key: str) -> bool:
        """Invalidate cache entry"""
        try:
            with self.lock:
                if key in self.cache_data:
                    del self.cache_data[key]
                    del self.cache_timestamps[key]
                    del self.cache_ttl[key]
            return True
        except Exception as e:
            logger.error(f"Failed to invalidate cache key {key}: {e}")
            return False
    
    def _cleanup_loop(self):
        """Background cleanup of expired cache entries"""
        while True:
            try:
                time.sleep(60)  # Cleanup every minute
                current_time = time.time()
                
                with self.lock:
                    expired_keys = [
                        key for key, timestamp in self.cache_timestamps.items()
                        if key in self.cache_ttl and current_time - timestamp > self.cache_ttl[key]
                    ]
                    
                    for key in expired_keys:
                        del self.cache_data[key]
                        del self.cache_timestamps[key]
                        del self.cache_ttl[key]
                    
                    if expired_keys:
                        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            
            except Exception as e:
                logger.error(f"Error in cache cleanup loop: {e}")

class ClusterManager:
    """Manages distributed computing cluster"""
    
    def __init__(self, cluster_id: str = None):
        self.cluster_id = cluster_id or str(uuid.uuid4())
        self.nodes: Dict[str, NodeInfo] = {}
        self.tasks: Dict[str, DistributedTask] = {}
        self.load_balancer = LoadBalancer()
        self.task_queue = TaskQueue()
        self.distributed_cache = DistributedCache()
        
        # Monitoring
        self.metrics_history: List[ClusterMetrics] = []
        self.heartbeat_interval = 30  # seconds
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
    
    def add_node(self, node_info: NodeInfo) -> bool:
        """Add a new node to the cluster"""
        try:
            if node_info.node_id in self.nodes:
                logger.warning(f"Node {node_info.node_id} already exists")
                return False
            
            self.nodes[node_info.node_id] = node_info
            logger.info(f"Added node {node_info.node_id} to cluster")
            return True
        except Exception as e:
            logger.error(f"Failed to add node {node_info.node_id}: {e}")
            return False
    
    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the cluster"""
        try:
            if node_id not in self.nodes:
                logger.warning(f"Node {node_id} not found")
                return False
            
            # Reassign tasks from this node
            self._reassign_node_tasks(node_id)
            
            del self.nodes[node_id]
            logger.info(f"Removed node {node_id} from cluster")
            return True
        except Exception as e:
            logger.error(f"Failed to remove node {node_id}: {e}")
            return False
    
    def submit_task(self, task: DistributedTask) -> bool:
        """Submit a task for distributed processing"""
        try:
            # Add to task queue
            if not self.task_queue.add_task(task):
                return False
            
            # Store task
            self.tasks[task.task_id] = task
            
            # Try to assign immediately if nodes are available
            self._process_pending_tasks()
            
            logger.info(f"Submitted task {task.task_id} for distributed processing")
            return True
        except Exception as e:
            logger.error(f"Failed to submit task {task.task_id}: {e}")
            return False
    
    def _process_pending_tasks(self):
        """Process pending tasks and assign to available nodes"""
        available_nodes = [
            node for node in self.nodes.values()
            if node.status == NodeStatus.ONLINE and node.current_load < 0.8
        ]
        
        if not available_nodes:
            return
        
        while True:
            task = self.task_queue.get_next_task()
            if not task:
                break
            
            # Select best node
            selected_node = self.load_balancer.select_node(available_nodes, task)
            if not selected_node:
                # Put task back in queue
                self.task_queue.add_task(task)
                break
            
            # Assign task to node
            task.assigned_node = selected_node.node_id
            task.status = "assigned"
            
            # Update node load
            selected_node.current_load += 0.1  # Rough estimate
            
            logger.info(f"Assigned task {task.task_id} to node {selected_node.node_id}")
    
    def _reassign_node_tasks(self, node_id: str):
        """Reassign tasks from a node that's being removed"""
        node_tasks = [
            task for task in self.tasks.values()
            if task.assigned_node == node_id and task.status in ["assigned", "running"]
        ]
        
        for task in node_tasks:
            task.assigned_node = None
            task.status = "pending"
            # Put back in queue
            self.task_queue.add_task(task)
        
        if node_tasks:
            logger.info(f"Reassigned {len(node_tasks)} tasks from node {node_id}")
    
    def _monitoring_loop(self):
        """Background monitoring of cluster health"""
        while True:
            try:
                time.sleep(self.heartbeat_interval)
                
                # Check node health
                current_time = datetime.now()
                for node_id, node in self.nodes.items():
                    time_since_heartbeat = (current_time - node.last_heartbeat).total_seconds()
                    
                    if time_since_heartbeat > self.heartbeat_interval * 2:
                        # Node seems offline
                        if node.status != NodeStatus.OFFLINE:
                            node.status = NodeStatus.OFFLINE
                            logger.warning(f"Node {node_id} marked as offline")
                    
                    # Update load based on assigned tasks
                    assigned_tasks = [
                        task for task in self.tasks.values()
                        if task.assigned_node == node_id and task.status in ["assigned", "running"]
                    ]
                    node.current_load = min(1.0, len(assigned_tasks) * 0.1)
                
                # Collect metrics
                self._collect_metrics()
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
    
    def _collect_metrics(self):
        """Collect cluster metrics"""
        try:
            active_nodes = [n for n in self.nodes.values() if n.status == NodeStatus.ONLINE]
            
            metrics = ClusterMetrics(
                total_nodes=len(self.nodes),
                active_nodes=len(active_nodes),
                total_cpu_cores=sum(n.cpu_cores for n in active_nodes),
                total_memory_gb=sum(n.memory_gb for n in active_nodes),
                average_load=sum(n.current_load for n in active_nodes) / len(active_nodes) if active_nodes else 0,
                tasks_queued=sum(self.task_queue.get_queue_status().values()),
                tasks_running=len([t for t in self.tasks.values() if t.status == "running"]),
                tasks_completed=len([t for t in self.tasks.values() if t.status == "completed"]),
                tasks_failed=len([t for t in self.tasks.values() if t.status == "failed"]),
                timestamp=datetime.now()
            )
            
            self.metrics_history.append(metrics)
            
            # Keep only last 1000 metrics
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
                
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get current cluster status"""
        return {
            "cluster_id": self.cluster_id,
            "total_nodes": len(self.nodes),
            "active_nodes": len([n for n in self.nodes.values() if n.status == NodeStatus.ONLINE]),
            "queue_status": self.task_queue.get_queue_status(),
            "recent_metrics": self.metrics_history[-10:] if self.metrics_history else [],
            "load_balancer_strategy": self.load_balancer.strategy
        }

# Convenience functions
def create_cluster_manager(cluster_id: str = None) -> ClusterManager:
    """Create and configure a cluster manager"""
    return ClusterManager(cluster_id)

def create_distributed_task(task_type: str, payload: Any, priority: TaskPriority = TaskPriority.NORMAL) -> DistributedTask:
    """Create a new distributed task"""
    return DistributedTask(
        task_id=str(uuid.uuid4()),
        task_type=task_type,
        payload=payload,
        priority=priority,
        created_at=datetime.now()
    )

def create_node_info(hostname: str, ip_address: str, port: int, cpu_cores: int, memory_gb: float) -> NodeInfo:
    """Create node information"""
    return NodeInfo(
        node_id=str(uuid.uuid4()),
        hostname=hostname,
        ip_address=ip_address,
        port=port,
        cpu_cores=cpu_cores,
        memory_gb=memory_gb,
        status=NodeStatus.ONLINE
    )
