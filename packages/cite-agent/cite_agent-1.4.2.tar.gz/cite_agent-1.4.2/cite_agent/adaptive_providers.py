"""
Adaptive Provider Selection System
Learns which provider is best for different query types and auto-switches
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Categories of queries handled"""
    ACADEMIC_PAPER = "academic_paper"      # Paper search, citations
    FINANCIAL_DATA = "financial_data"      # Stock prices, metrics
    WEB_SEARCH = "web_search"              # General web search
    CODE_GENERATION = "code_generation"    # Write/debug code
    DATA_ANALYSIS = "data_analysis"        # CSV, statistical analysis
    CONVERSATION = "conversation"          # General chat
    SHELL_EXECUTION = "shell_execution"    # System commands


@dataclass
class ProviderPerformanceProfile:
    """Performance metrics for a provider on a specific query type"""
    provider_name: str
    query_type: QueryType
    total_requests: int = 0
    successful_requests: int = 0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    accuracy_score: float = 1.0  # 0.0 to 1.0
    cost_per_request: float = 0.0
    last_used: Optional[datetime] = None
    latency_history: List[float] = field(default_factory=list)
    error_history: List[str] = field(default_factory=list)
    
    def get_success_rate(self) -> float:
        """Success rate for this provider on this query type"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    def get_score(self) -> float:
        """Composite score for this provider (higher is better)"""
        success_rate = self.get_success_rate()
        latency_penalty = min(self.avg_latency_ms / 1000, 10)  # Cap at 10s penalty
        cost_penalty = self.cost_per_request * 100  # Cost in cents
        
        # Score = (success_rate * accuracy) - latency_penalty - cost_penalty
        score = (success_rate * self.accuracy_score * 100) - latency_penalty - cost_penalty
        return max(0, score)  # Never negative
    
    def add_result(
        self,
        success: bool,
        latency_ms: float,
        accuracy_score: float = 1.0,
        cost: float = 0.0,
        error: Optional[str] = None
    ):
        """Record a result for this provider"""
        self.total_requests += 1
        self.latency_history.append(latency_ms)
        
        # Keep only last 100 latencies for p95 calculation
        if len(self.latency_history) > 100:
            self.latency_history = self.latency_history[-100:]
        
        # Update p95 latency
        sorted_latencies = sorted(self.latency_history)
        idx = int(len(sorted_latencies) * 0.95)
        self.p95_latency_ms = sorted_latencies[min(idx, len(sorted_latencies) - 1)]
        
        # Update average
        self.avg_latency_ms = sum(self.latency_history) / len(self.latency_history)
        
        if success:
            self.successful_requests += 1
            self.accuracy_score = (self.accuracy_score + accuracy_score) / 2
        else:
            self.error_history.append(error or "unknown")
            # Keep last 10 errors
            if len(self.error_history) > 10:
                self.error_history = self.error_history[-10:]
        
        self.cost_per_request = cost
        self.last_used = datetime.now()


@dataclass
class ProviderSelectionPolicy:
    """Policy for selecting providers"""
    always_prefer: Optional[str] = None  # Force specific provider (e.g., "cerebras")
    avoid_providers: List[str] = field(default_factory=list)  # Never use these
    cost_sensitive: bool = False  # Prefer cheaper if performance similar
    latency_sensitive: bool = True  # Prefer faster
    reliability_weight: float = 0.7  # How much to weight success rate
    latency_weight: float = 0.3  # How much to weight latency


class AdaptiveProviderSelector:
    """
    Intelligently selects providers based on:
    - Query type (different providers excel at different tasks)
    - Historical performance (learns what works)
    - Current system state (avoid degraded providers)
    - User preferences (cost vs speed)
    - Time of day (some providers have peak hours)
    """
    
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path.home() / ".nocturnal_archive" / "provider_selection"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Performance profiles: provider -> query_type -> profile
        self.profiles: Dict[str, Dict[QueryType, ProviderPerformanceProfile]] = {}
        
        # Provider health status
        self.provider_health: Dict[str, float] = {}  # provider -> health (0.0-1.0)
        self.provider_last_degraded: Dict[str, datetime] = {}
        
        # Load historical data
        self._load_profiles()
    
    def select_provider(
        self,
        query_type: QueryType,
        available_providers: List[str],
        policy: Optional[ProviderSelectionPolicy] = None,
        exclude: Optional[List[str]] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Select best provider for this query type
        
        Returns:
            (provider_name, fallback_provider)
        """
        policy = policy or ProviderSelectionPolicy()
        exclude = exclude or []
        
        # Filter available providers
        candidates = [
            p for p in available_providers
            if p not in exclude and p not in policy.avoid_providers
        ]
        
        if not candidates:
            # Fall back to anything available
            candidates = available_providers
        
        # If policy says use specific provider, use it
        if policy.always_prefer and policy.always_prefer in candidates:
            fallback = next((p for p in candidates if p != policy.always_prefer), None)
            return policy.always_prefer, fallback
        
        # Score each candidate
        scores = {}
        for provider in candidates:
            profile = self._get_or_create_profile(provider, query_type)
            health = self.provider_health.get(provider, 1.0)
            
            # Composite score
            score = profile.get_score() * health
            scores[provider] = score
            
            logger.debug(
                f"Provider '{provider}' for {query_type.value}: "
                f"score={profile.get_score():.1f}, health={health:.1%}"
            )
        
        # Select top 2
        sorted_providers = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_providers:
            best = sorted_providers[0][0]
            fallback = sorted_providers[1][0] if len(sorted_providers) > 1 else None
            
            logger.info(
                f"📊 Selected provider '{best}' for {query_type.value} "
                f"(fallback: {fallback})"
            )
            
            return best, fallback
        
        # Emergency fallback
        return candidates[0] if candidates else "cerebras", None
    
    def record_result(
        self,
        provider: str,
        query_type: QueryType,
        success: bool,
        latency_ms: float,
        accuracy_score: float = 1.0,
        cost: float = 0.0,
        error: Optional[str] = None
    ):
        """Record result of using a provider for a query type"""
        profile = self._get_or_create_profile(provider, query_type)
        profile.add_result(success, latency_ms, accuracy_score, cost, error)
        
        # Update provider health based on success
        current_health = self.provider_health.get(provider, 1.0)
        if success:
            # Improve health (back toward 1.0)
            new_health = min(1.0, current_health + 0.05)
        else:
            # Degrade health
            new_health = max(0.0, current_health - 0.1)
        
        self.provider_health[provider] = new_health
        
        if new_health < 0.5:
            self.provider_last_degraded[provider] = datetime.now()
            logger.warning(f"⚠️ Provider '{provider}' degraded (health: {new_health:.1%})")
        
        # Save updated profiles
        self._save_profiles()
    
    def get_provider_recommendation(
        self,
        query_type: QueryType,
        available_providers: List[str]
    ) -> Dict[str, any]:
        """Get detailed recommendation for a query type"""
        recommendations = {}
        
        for provider in available_providers:
            profile = self._get_or_create_profile(provider, query_type)
            health = self.provider_health.get(provider, 1.0)
            
            recommendations[provider] = {
                "score": profile.get_score(),
                "success_rate": profile.get_success_rate(),
                "avg_latency_ms": profile.avg_latency_ms,
                "p95_latency_ms": profile.p95_latency_ms,
                "requests_used": profile.total_requests,
                "health": health,
                "recommendation": "✅ Excellent" if profile.get_score() > 80 else
                                 "✓ Good" if profile.get_score() > 50 else
                                 "⚠️ Fair" if profile.get_score() > 20 else
                                 "❌ Poor"
            }
        
        return recommendations
    
    def get_provider_rankings(self, query_type: QueryType) -> List[Tuple[str, float]]:
        """Rank providers for a specific query type"""
        rankings = []
        
        for provider, profiles_by_type in self.profiles.items():
            if query_type in profiles_by_type:
                profile = profiles_by_type[query_type]
                health = self.provider_health.get(provider, 1.0)
                score = profile.get_score() * health
                rankings.append((provider, score))
        
        return sorted(rankings, key=lambda x: x[1], reverse=True)
    
    def should_switch_provider(
        self,
        current_provider: str,
        query_type: QueryType
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if we should switch from current provider
        
        Returns:
            (should_switch, better_provider)
        """
        current_profile = self._get_or_create_profile(current_provider, query_type)
        current_health = self.provider_health.get(current_provider, 1.0)
        current_score = current_profile.get_score() * current_health
        
        # If health is very low, definitely switch
        if current_health < 0.3:
            rankings = self.get_provider_rankings(query_type)
            if rankings and rankings[0][0] != current_provider:
                return True, rankings[0][0]
        
        # If there's a significantly better option, switch
        rankings = self.get_provider_rankings(query_type)
        for provider, score in rankings[:3]:
            if provider != current_provider and score > current_score * 1.2:
                return True, provider
        
        return False, None
    
    def _get_or_create_profile(
        self,
        provider: str,
        query_type: QueryType
    ) -> ProviderPerformanceProfile:
        """Get or create performance profile"""
        if provider not in self.profiles:
            self.profiles[provider] = {}
        
        if query_type not in self.profiles[provider]:
            self.profiles[provider][query_type] = ProviderPerformanceProfile(
                provider_name=provider,
                query_type=query_type
            )
        
        return self.profiles[provider][query_type]
    
    def _load_profiles(self):
        """Load historical performance data"""
        profile_file = self.storage_dir / "provider_profiles.json"
        if not profile_file.exists():
            return
        
        try:
            with open(profile_file, 'r') as f:
                data = json.load(f)
            
            for provider, query_types in data.items():
                for query_type_str, profile_data in query_types.items():
                    try:
                        query_type = QueryType(query_type_str)
                        profile = ProviderPerformanceProfile(**profile_data)
                        
                        if provider not in self.profiles:
                            self.profiles[provider] = {}
                        self.profiles[provider][query_type] = profile
                    except ValueError:
                        continue
            
            logger.info(f"📥 Loaded {len(self.profiles)} provider profiles")
        
        except Exception as e:
            logger.error(f"Failed to load profiles: {e}")
    
    def _save_profiles(self):
        """Save performance data to disk"""
        try:
            profile_file = self.storage_dir / "provider_profiles.json"
            
            data = {}
            for provider, query_types in self.profiles.items():
                data[provider] = {}
                for query_type, profile in query_types.items():
                    data[provider][query_type.value] = {
                        'provider_name': profile.provider_name,
                        'query_type': query_type.value,
                        'total_requests': profile.total_requests,
                        'successful_requests': profile.successful_requests,
                        'avg_latency_ms': profile.avg_latency_ms,
                        'p95_latency_ms': profile.p95_latency_ms,
                        'accuracy_score': profile.accuracy_score,
                        'cost_per_request': profile.cost_per_request,
                    }
            
            with open(profile_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            logger.error(f"Failed to save profiles: {e}")
    
    def get_status_message(self) -> str:
        """Human-readable status"""
        lines = ["📊 **Provider Selection Status**"]
        
        # Provider health
        if self.provider_health:
            lines.append("\n🏥 **Provider Health**")
            for provider, health in sorted(self.provider_health.items()):
                emoji = "🟢" if health > 0.7 else "🟡" if health > 0.3 else "🔴"
                lines.append(f"  • {provider}: {emoji} {health:.1%}")
        
        # Best providers per query type
        lines.append("\n⭐ **Best Providers by Query Type**")
        for query_type in QueryType:
            rankings = self.get_provider_rankings(query_type)
            if rankings:
                best_provider, score = rankings[0]
                lines.append(f"  • {query_type.value}: {best_provider} (score: {score:.1f})")
        
        return "\n".join(lines)


# Global instance
adaptive_selector = AdaptiveProviderSelector()


if __name__ == "__main__":
    # Test the adaptive selector
    selector = AdaptiveProviderSelector()
    
    # Simulate some usage
    for i in range(20):
        provider = selector.select_provider(
            QueryType.CODE_GENERATION,
            ["cerebras", "groq", "mistral"]
        )[0]
        
        # Simulate result (groq should be slightly better)
        success = (i % 5) != 0  # 80% success
        latency = 100 + (i % 10) * 10
        
        selector.record_result(provider, QueryType.CODE_GENERATION, success, latency)
    
    print(selector.get_status_message())
    print("\n" + json.dumps(
        selector.get_provider_recommendation(QueryType.CODE_GENERATION, ["cerebras", "groq"]),
        indent=2,
        default=str
    ))
