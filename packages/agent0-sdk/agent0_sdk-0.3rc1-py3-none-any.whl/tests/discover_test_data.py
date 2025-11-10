"""
Temporary script to discover test data from all subgraph chains.
Downloads feedback data and finds agents with useful attributes for testing.
"""

import json
import sys
from typing import Dict, List, Any, Set
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, '/Users/madero/Documents/Agent0-sdk/agent0-py')

from agent0_sdk import SDK, SearchParams
from agent0_sdk.core.contracts import DEFAULT_SUBGRAPH_URLS

# Supported chains
SUPPORTED_CHAINS = [11155111, 84532, 80002]  # ETH Sepolia, Base Sepolia, Polygon Amoy

# RPC URLs (only needed for SDK initialization, not used for subgraph queries)
RPC_URLS = {
    11155111: "https://eth-sepolia.g.alchemy.com/v2/7nkA4bJ0tKWcl2-5Wn15c5eRdpGZ8DDr",
    84532: "https://base-sepolia.g.alchemy.com/v2/7nkA4bJ0tKWcl2-5Wn15c5eRdpGZ8DDr",
    80002: "https://polygon-amoy.g.alchemy.com/v2/7nkA4bJ0tKWcl2-5Wn15c5eRdpGZ8DDr",
}


def discover_agents_with_feedback(sdk: SDK, chain_id: int) -> List[Dict[str, Any]]:
    """Discover agents that have feedback on a specific chain."""
    print(f"\n🔍 Discovering agents with feedback on chain {chain_id}...")
    
    agents_with_feedback = []
    
    try:
        # Search for agents on this chain
        params = SearchParams()
        params.chains = [chain_id]
        search_result = sdk.indexer.search_agents(params, sort=[], page_size=100)
        
        agents = search_result.get('items', [])
        print(f"   Found {len(agents)} total agents on chain {chain_id}")
        
        # Check each agent for feedback
        for agent in agents:
            # Handle both dict and AgentSummary objects
            if isinstance(agent, dict):
                agent_id = agent.get('agentId') or agent.get('id')
                agent_name = agent.get('name', 'Unknown')
            else:
                agent_id = agent.agentId
                agent_name = agent.name
            try:
                # Try to get feedback for this agent
                feedbacks = sdk.indexer.search_feedback(
                    agentId=agent_id,
                    first=1,  # Just check if any feedback exists
                    skip=0
                )
                
                if feedbacks and len(feedbacks) > 0:
                    # Get full feedback count
                    all_feedbacks = sdk.indexer.search_feedback(
                        agentId=agent_id,
                        first=1000,  # Get all feedback
                        skip=0
                    )
                    
                    agents_with_feedback.append({
                        'chainId': chain_id,
                        'agentId': agent_id,
                        'name': agent_name,
                        'description': agent.get('description', '') if isinstance(agent, dict) else (agent.description if hasattr(agent, 'description') else ''),
                        'feedbackCount': len(all_feedbacks),
                        'feedbacks': all_feedbacks[:10],  # Store first 10 for analysis
                        'agent': agent
                    })
                    print(f"   ✅ {agent_name} ({agent_id}): {len(all_feedbacks)} feedback entries")
            except Exception as e:
                # Skip agents that error
                continue
        
        print(f"   Total agents with feedback: {len(agents_with_feedback)}")
        
    except Exception as e:
        print(f"   ❌ Error discovering agents: {e}")
    
    return agents_with_feedback


def analyze_feedback_data(agents_with_feedback: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze feedback data to extract useful test attributes."""
    print(f"\n📊 Analyzing feedback data...")
    
    analysis = {
        'totalAgents': len(agents_with_feedback),
        'totalFeedback': 0,
        'tags': defaultdict(int),
        'capabilities': defaultdict(int),
        'skills': defaultdict(int),
        'tasks': defaultdict(int),
        'scores': [],
        'agents_by_chain': defaultdict(list),
        'agents_with_high_scores': [],
        'agents_with_tags': defaultdict(list),
        'agents_with_capabilities': defaultdict(list),
        'agents_with_skills': defaultdict(list),
    }
    
    for agent_data in agents_with_feedback:
        chain_id = agent_data['chainId']
        agent_id = agent_data['agentId']
        feedbacks = agent_data['feedbacks']
        
        analysis['totalFeedback'] += agent_data['feedbackCount']
        analysis['agents_by_chain'][chain_id].append(agent_id)
        
        # Analyze each feedback entry
        scores = []
        for feedback in feedbacks:
            # Collect scores
            if feedback.score is not None:
                scores.append(feedback.score)
                analysis['scores'].append(feedback.score)
            
            # Collect tags
            if feedback.tags:
                for tag in feedback.tags:
                    analysis['tags'][tag] += 1
                    if agent_id not in analysis['agents_with_tags'][tag]:
                        analysis['agents_with_tags'][tag].append(agent_id)
            
            # Collect capabilities
            if feedback.capability:
                analysis['capabilities'][feedback.capability] += 1
                if agent_id not in analysis['agents_with_capabilities'][feedback.capability]:
                    analysis['agents_with_capabilities'][feedback.capability].append(agent_id)
            
            # Collect skills
            if feedback.skill:
                analysis['skills'][feedback.skill] += 1
                if agent_id not in analysis['agents_with_skills'][feedback.skill]:
                    analysis['agents_with_skills'][feedback.skill].append(agent_id)
            
            # Collect tasks
            if feedback.task:
                analysis['tasks'][feedback.task] += 1
        
        # Calculate average score for this agent
        if scores:
            avg_score = sum(scores) / len(scores)
            if avg_score >= 70:  # High score threshold
                analysis['agents_with_high_scores'].append({
                    'agentId': agent_id,
                    'chainId': chain_id,
                    'name': agent_data['name'],
                    'avgScore': avg_score,
                    'feedbackCount': agent_data['feedbackCount']
                })
    
    return analysis


def discover_agents_by_reputation(sdk: SDK, chain_id: int) -> List[Dict[str, Any]]:
    """Discover agents using reputation search."""
    print(f"\n⭐ Discovering agents by reputation on chain {chain_id}...")
    
    agents = []
    
    try:
        result = sdk.searchAgentsByReputation(
            page_size=50,
            chains=[chain_id]
        )
        
        found_agents = result.get('items', [])
        print(f"   Found {len(found_agents)} agents by reputation")
        
        for agent in found_agents:
            avg_score = agent.extras.get('averageScore') if agent.extras else None
            agents.append({
                'chainId': chain_id,
                'agentId': agent.agentId,
                'name': agent.name,
                'averageScore': avg_score,
                'agent': agent
            })
            if avg_score:
                print(f"   ✅ {agent.name} ({agent.agentId}): Avg Score {avg_score:.2f}")
            else:
                print(f"   ⚠️  {agent.name} ({agent.agentId}): No average score")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return agents


def discover_agents_with_attributes(sdk: SDK, chain_id: int) -> Dict[str, List[Dict[str, Any]]]:
    """Discover agents with specific attributes (MCP tools, A2A skills, etc.)."""
    print(f"\n🎯 Discovering agents with attributes on chain {chain_id}...")
    
    attributes = {
        'with_mcp_tools': [],
        'with_a2a_skills': [],
        'with_ens': [],
        'with_wallet': [],
        'active': [],
        'x402support': [],
    }
    
    try:
        params = SearchParams()
        params.chains = [chain_id]
        search_result = sdk.indexer.search_agents(params, sort=[], page_size=100)
        
        agents = search_result.get('items', [])
        
        for agent in agents:
            # Handle both dict and AgentSummary objects
            if isinstance(agent, dict):
                agent_id = agent.get('agentId') or agent.get('id')
                agent_name = agent.get('name', 'Unknown')
                agent_mcp = agent.get('mcp', False)
                agent_a2a = agent.get('a2a', False)
                agent_ens = agent.get('ens')
                agent_wallet = agent.get('walletAddress')
                agent_active = agent.get('active', False)
                agent_x402 = agent.get('x402support', False)
                mcp_tools = agent.get('mcpTools', [])
                a2a_skills = agent.get('a2aSkills', [])
            else:
                agent_id = agent.agentId
                agent_name = agent.name
                agent_mcp = agent.mcp
                agent_a2a = agent.a2a
                agent_ens = agent.ens
                agent_wallet = agent.walletAddress
                agent_active = agent.active
                agent_x402 = agent.x402support
                mcp_tools = agent.mcpTools if hasattr(agent, 'mcpTools') else []
                a2a_skills = agent.a2aSkills if hasattr(agent, 'a2aSkills') else []
            
            agent_info = {
                'chainId': chain_id,
                'agentId': agent_id,
                'name': agent_name,
            }
            
            if agent_mcp and mcp_tools:
                attributes['with_mcp_tools'].append({
                    **agent_info,
                    'mcpTools': mcp_tools
                })
            
            if agent_a2a and a2a_skills:
                attributes['with_a2a_skills'].append({
                    **agent_info,
                    'a2aSkills': a2a_skills
                })
            
            if agent_ens:
                attributes['with_ens'].append({
                    **agent_info,
                    'ens': agent_ens
                })
            
            if agent_wallet:
                attributes['with_wallet'].append({
                    **agent_info,
                    'walletAddress': agent_wallet
                })
            
            if agent_active:
                attributes['active'].append(agent_info)
            
            if agent_x402:
                attributes['x402support'].append(agent_info)
        
        # Print summary
        for attr_name, attr_list in attributes.items():
            if attr_list:
                print(f"   {attr_name}: {len(attr_list)} agents")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return attributes


def main():
    print("=" * 80)
    print("🔍 DISCOVERING TEST DATA FROM ALL SUBGRAPH CHAINS")
    print("=" * 80)
    
    all_agents_with_feedback = []
    all_reputation_agents = []
    all_attributes = defaultdict(lambda: defaultdict(list))
    
    # Process each chain
    for chain_id in SUPPORTED_CHAINS:
        print(f"\n{'='*80}")
        print(f"📡 Processing Chain {chain_id}")
        print(f"{'='*80}")
        
        # Initialize SDK for this chain
        # Use ETH Sepolia RPC for all chains (only needed for SDK init, not used for subgraph queries)
        try:
            sdk = SDK(
                chainId=chain_id,
                rpcUrl=RPC_URLS[11155111],  # Use working RPC for all
                signer=None  # Read-only
            )
        except Exception as e:
            print(f"   ⚠️  Failed to initialize SDK for chain {chain_id}: {e}")
            print(f"   Skipping chain {chain_id}")
            continue
        
        # 1. Discover agents with feedback
        agents_with_feedback = discover_agents_with_feedback(sdk, chain_id)
        all_agents_with_feedback.extend(agents_with_feedback)
        
        # 2. Discover agents by reputation
        reputation_agents = discover_agents_by_reputation(sdk, chain_id)
        all_reputation_agents.extend(reputation_agents)
        
        # 3. Discover agents with attributes
        attributes = discover_agents_with_attributes(sdk, chain_id)
        for attr_name, attr_list in attributes.items():
            all_attributes[chain_id][attr_name] = attr_list
    
    # Analyze all collected data
    print(f"\n{'='*80}")
    print("📊 COMPREHENSIVE ANALYSIS")
    print(f"{'='*80}")
    
    analysis = analyze_feedback_data(all_agents_with_feedback)
    
    # Print summary
    print(f"\n📈 SUMMARY:")
    print(f"   Total agents with feedback: {analysis['totalAgents']}")
    print(f"   Total feedback entries: {analysis['totalFeedback']}")
    print(f"   Agents by chain: {dict(analysis['agents_by_chain'])}")
    
    # Top tags
    if analysis['tags']:
        print(f"\n🏷️  TOP TAGS (for testing):")
        sorted_tags = sorted(analysis['tags'].items(), key=lambda x: x[1], reverse=True)[:10]
        for tag, count in sorted_tags:
            agents_with_tag = analysis['agents_with_tags'][tag]
            print(f"   '{tag}': {count} feedback entries, {len(agents_with_tag)} agents")
            if agents_with_tag:
                print(f"      Example agents: {agents_with_tag[:3]}")
    
    # Top capabilities
    if analysis['capabilities']:
        print(f"\n🛠️  TOP CAPABILITIES (for testing):")
        sorted_caps = sorted(analysis['capabilities'].items(), key=lambda x: x[1], reverse=True)[:10]
        for cap, count in sorted_caps:
            agents_with_cap = analysis['agents_with_capabilities'][cap]
            print(f"   '{cap}': {count} feedback entries, {len(agents_with_cap)} agents")
            if agents_with_cap:
                print(f"      Example agents: {agents_with_cap[:3]}")
    
    # Top skills
    if analysis['skills']:
        print(f"\n💡 TOP SKILLS (for testing):")
        sorted_skills = sorted(analysis['skills'].items(), key=lambda x: x[1], reverse=True)[:10]
        for skill, count in sorted_skills:
            agents_with_skill = analysis['agents_with_skills'][skill]
            print(f"   '{skill}': {count} feedback entries, {len(agents_with_skill)} agents")
            if agents_with_skill:
                print(f"      Example agents: {agents_with_skill[:3]}")
    
    # Agents with high scores
    if analysis['agents_with_high_scores']:
        print(f"\n⭐ AGENTS WITH HIGH SCORES (avg >= 70):")
        sorted_high = sorted(analysis['agents_with_high_scores'], key=lambda x: x['avgScore'], reverse=True)[:10]
        for agent_info in sorted_high:
            print(f"   {agent_info['name']} ({agent_info['agentId']}): {agent_info['avgScore']:.2f} ({agent_info['feedbackCount']} feedback)")
    
    # Reputation agents summary
    if all_reputation_agents:
        print(f"\n⭐ REPUTATION SEARCH RESULTS:")
        agents_with_scores = [a for a in all_reputation_agents if a.get('averageScore')]
        if agents_with_scores:
            print(f"   Found {len(agents_with_scores)} agents with reputation scores")
            sorted_reputation = sorted(agents_with_scores, key=lambda x: x.get('averageScore', 0) or 0, reverse=True)[:10]
            for agent_info in sorted_reputation:
                print(f"   {agent_info['name']} ({agent_info['agentId']}): {agent_info['averageScore']:.2f}")
    
    # Save detailed data to JSON file
    output_data = {
        'agents_with_feedback': [
            {
                'chainId': a['chainId'],
                'agentId': a['agentId'],
                'name': a['name'],
                'feedbackCount': a['feedbackCount'],
            }
            for a in all_agents_with_feedback
        ],
        'reputation_agents': all_reputation_agents,
        'attributes_by_chain': {
            chain_id: {
                attr_name: attr_list
                for attr_name, attr_list in attrs.items()
            }
            for chain_id, attrs in all_attributes.items()
        },
        'analysis': {
            'totalAgents': analysis['totalAgents'],
            'totalFeedback': analysis['totalFeedback'],
            'topTags': dict(sorted(analysis['tags'].items(), key=lambda x: x[1], reverse=True)[:20]),
            'topCapabilities': dict(sorted(analysis['capabilities'].items(), key=lambda x: x[1], reverse=True)[:20]),
            'topSkills': dict(sorted(analysis['skills'].items(), key=lambda x: x[1], reverse=True)[:20]),
            'agents_by_chain': {str(k): v for k, v in analysis['agents_by_chain'].items()},
            'agents_with_high_scores': analysis['agents_with_high_scores'],
            'example_agents_with_tags': {
                tag: agents[:5]
                for tag, agents in list(analysis['agents_with_tags'].items())[:10]
            },
            'example_agents_with_capabilities': {
                cap: agents[:5]
                for cap, agents in list(analysis['agents_with_capabilities'].items())[:10]
            },
            'example_agents_with_skills': {
                skill: agents[:5]
                for skill, agents in list(analysis['agents_with_skills'].items())[:10]
            },
        }
    }
    
    output_file = '/Users/madero/Documents/Agent0-sdk/agent0-py/tests/test_data_discovery.json'
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)
    
    print(f"\n💾 Detailed data saved to: {output_file}")
    print(f"\n{'='*80}")
    print("✅ DISCOVERY COMPLETE")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()

