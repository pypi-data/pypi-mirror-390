#!/usr/bin/env python3
"""
DeepSeek R1 Local Web Application - Ultra-Optimized Version with Web Search
"""
import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import json
import time
import hashlib
from functools import lru_cache
from collections import OrderedDict
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

app = Flask(__name__)
CORS(app)

# Get the script directory for relative paths
SCRIPT_DIR = Path(__file__).parent.absolute()
MODEL_DIR = SCRIPT_DIR / "models" / "deepseek-r1"
model = None
tokenizer = None

class ResponseCache:
    """LRU cache for responses"""
    def __init__(self, maxsize=100):
        self.cache = OrderedDict()
        self.maxsize = maxsize
    
    def get_key(self, prompt, max_length, temperature):
        """Generate cache key"""
        key_str = f"{prompt}:{max_length}:{temperature:.2f}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, prompt, max_length, temperature):
        """Get cached response"""
        key = self.get_key(prompt, max_length, temperature)
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def set(self, prompt, max_length, temperature, response):
        """Cache response"""
        key = self.get_key(prompt, max_length, temperature)
        self.cache[key] = response
        self.cache.move_to_end(key)
        
        # Remove oldest if over size
        if len(self.cache) > self.maxsize:
            self.cache.popitem(last=False)

class WebSearcher:
    """Web search functionality using DuckDuckGo"""
    def __init__(self):
        self.ddgs = DDGS()
    
    def search(self, query, max_results=5):
        """Search the web and return results"""
        try:
            print(f"Searching web for: {query}")
            results = []
            
            # Search with DuckDuckGo
            search_results = self.ddgs.text(query, max_results=max_results)
            
            for result in search_results:
                results.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('body', ''),
                    'url': result.get('href', '')
                })
            
            print(f"Found {len(results)} results")
            return results
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def format_search_results(self, results):
        """Format search results for the model"""
        if not results:
            return "No search results found."
        
        formatted = "Web search results:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\n"
            formatted += f"   {result['snippet']}\n"
            formatted += f"   Source: {result['url']}\n\n"
        
        return formatted

class CouncilMember:
    """Represents a council member with a unique perspective"""
    def __init__(self, name, role, personality, approach):
        self.name = name
        self.role = role
        self.personality = personality
        self.approach = approach
        self.opinion = None
        self.vote = None

class Council:
    """Council deliberation system with 5 diverse personas"""
    def __init__(self):
        self.members = [
            CouncilMember(
                name="Dr. Logic",
                role="The Analytical Rationalist",
                personality="Methodical, data-driven, focuses on facts and logical consistency",
                approach="Breaks down problems systematically, seeks empirical evidence"
            ),
            CouncilMember(
                name="Professor Sage",
                role="The Historical Scholar",
                personality="Wise, thoughtful, draws from past experiences and patterns",
                approach="References historical precedents, considers long-term implications"
            ),
            CouncilMember(
                name="Innovator Nova",
                role="The Creative Visionary",
                personality="Bold, imaginative, challenges conventional thinking",
                approach="Proposes novel solutions, embraces unconventional perspectives"
            ),
            CouncilMember(
                name="Advocate Heart",
                role="The Empathetic Humanist",
                personality="Compassionate, people-focused, considers emotional impact",
                approach="Prioritizes human welfare, ethical considerations, social impact"
            ),
            CouncilMember(
                name="Pragmatist Ray",
                role="The Practical Realist",
                personality="Down-to-earth, action-oriented, focuses on feasibility",
                approach="Evaluates practicality, resource constraints, real-world application"
            )
        ]
    
    def deliberate(self, prompt, model_manager):
        """Run a full council deliberation"""
        results = {
            'prompt': prompt,
            'members': [],
            'deliberation': '',
            'votes': {},
            'winning_proposal': None,
            'final_decision': ''
        }
        
        print(f"\n{'='*60}")
        print("COUNCIL DELIBERATION IN SESSION")
        print(f"{'='*60}")
        print(f"Topic: {prompt}\n")
        
        # Phase 1: Individual Proposals
        print("Phase 1: Individual Council Member Proposals\n")
        for i, member in enumerate(self.members):
            proposal_prompt = f"""You are {member.name}, {member.role}.
Personality: {member.personality}
Approach: {member.approach}

The question is: {prompt}

Provide your specific recommendation or answer in 2-3 sentences from your unique perspective. Be concrete and actionable."""
            
            print(f"  {member.name} is formulating their proposal...")
            member.opinion = model_manager.generate_response(
                proposal_prompt, 
                max_length=100, 
                temperature=0.7,
                web_search=False
            )
            
            results['members'].append({
                'name': member.name,
                'role': member.role,
                'proposal_id': i,
                'proposal': member.opinion
            })
            
            print(f"  ✓ {member.name}: {member.opinion[:80]}...")
        
        # Phase 2: Deliberation - Compare proposals
        print(f"\nPhase 2: Council Deliberation & Comparison\n")
        all_proposals = "\n\n".join([
            f"PROPOSAL {i} by {m.name} ({m.role}): {m.opinion}" 
            for i, m in enumerate(self.members)
        ])
        
        deliberation_prompt = f"""The council is deliberating on: {prompt}

Here are the 5 proposals:
{all_proposals}

Analyze the key differences between these proposals. Which proposals are similar? Which are fundamentally different? (3-4 sentences)"""
        
        print("  Council is deliberating...")
        results['deliberation'] = model_manager.generate_response(
            deliberation_prompt,
            max_length=150,
            temperature=0.5,
            web_search=False
        )
        print(f"  ✓ Deliberation complete")
        
        # Phase 3: Voting - Each member distributes 5 votes across OTHER proposals
        print(f"\nPhase 3: Council Vote (Each member has 5 votes for OTHER proposals)\n")
        proposal_votes = {i: 0 for i in range(len(self.members))}
        
        for i, member in enumerate(self.members):
            # Present ONLY other members' proposals (not their own)
            other_proposals = "\n\n".join([
                f"PROPOSAL {j} by {self.members[j].name}: {self.members[j].opinion}"
                for j in range(len(self.members)) if j != i
            ])
            
            vote_prompt = f"""As {member.name}, you've reviewed all proposals on: {prompt}

YOUR proposal was: {member.opinion}

Now read the OTHER council members' proposals:
{other_proposals}

You have 5 votes to distribute among these OTHER proposals (you cannot vote for your own).
You can give multiple votes to one proposal or spread them out based on merit.

Distribute your 5 votes among the OTHER proposals. Format EXACTLY:
PROPOSAL X: Y votes
PROPOSAL X: Y votes
(List only proposals you're voting for, votes must sum to 5)

Then explain your reasoning in 1-2 sentences."""
            
            vote_response = model_manager.generate_response(
                vote_prompt,
                max_length=120,
                temperature=0.4,
                web_search=False
            )
            
            # Parse vote distribution
            member_vote_distribution = {j: 0 for j in range(len(self.members))}
            total_votes_cast = 0
            
            # Try to parse the vote distribution
            import re
            for j in range(len(self.members)):
                if j == i:  # Skip their own proposal
                    continue
                    
                # Look for patterns like "PROPOSAL X: Y votes" or "PROPOSAL X: Y"
                patterns = [
                    rf"PROPOSAL\s*{j}\s*:?\s*(\d+)",
                    rf"proposal\s*{j}\s*:?\s*(\d+)",
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, vote_response, re.IGNORECASE)
                    if matches:
                        try:
                            votes = int(matches[0])
                            if votes > 0:
                                member_vote_distribution[j] = votes
                                total_votes_cast += votes
                            break
                        except:
                            pass
            
            # If parsing failed or votes don't sum to 5, distribute among others fairly
            if total_votes_cast != 5:
                print(f"    (Adjusting {member.name}'s votes: {total_votes_cast} → 5)")
                member_vote_distribution = {j: 0 for j in range(len(self.members))}
                # Distribute 5 votes among other 4 members (can't have more than 4 other members)
                other_indices = [j for j in range(len(self.members)) if j != i]
                if len(other_indices) >= 3:
                    member_vote_distribution[other_indices[0]] = 2
                    member_vote_distribution[other_indices[1]] = 2
                    member_vote_distribution[other_indices[2]] = 1
                elif len(other_indices) == 2:
                    member_vote_distribution[other_indices[0]] = 3
                    member_vote_distribution[other_indices[1]] = 2
                elif len(other_indices) == 1:
                    member_vote_distribution[other_indices[0]] = 5
                
                # Recalculate total
                total_votes_cast = sum(member_vote_distribution.values())
            
            # Ensure they didn't vote for themselves
            if member_vote_distribution[i] > 0:
                print(f"    (Removing {member.name}'s {member_vote_distribution[i]} self-votes)")
                member_vote_distribution[i] = 0
                # Recalculate and adjust if needed
                total_votes_cast = sum(member_vote_distribution.values())
            
            # Final validation: ensure exactly 5 votes
            actual_total = sum(member_vote_distribution.values())
            if actual_total != 5:
                print(f"    (ERROR: {member.name} has {actual_total} votes, expected 5. Re-adjusting...)")
                member_vote_distribution = {j: 0 for j in range(len(self.members))}
                other_indices = [j for j in range(len(self.members)) if j != i]
                member_vote_distribution[other_indices[0]] = 2
                member_vote_distribution[other_indices[1]] = 2
                member_vote_distribution[other_indices[2]] = 1
            
            # Add votes to totals
            for j, votes in member_vote_distribution.items():
                proposal_votes[j] += votes
            
            member.vote = member_vote_distribution
            
            results['votes'][member.name] = {
                'distribution': member_vote_distribution,
                'response': vote_response
            }
            
            # Display vote distribution (only show non-zero votes)
            vote_summary = ", ".join([
                f"P{j}({self.members[j].name}):{v}" for j, v in member_vote_distribution.items() if v > 0
            ])
            print(f"  {member.name}: {vote_summary}")
        
        # Phase 4: Final Decision - Use the winning proposal verbatim
        print(f"\nPhase 4: Final Decision\n")
        
        # Find winning proposal
        winning_proposal_id = max(proposal_votes, key=proposal_votes.get)
        winning_member = self.members[winning_proposal_id]
        winning_votes = proposal_votes[winning_proposal_id]
        
        results['winning_proposal'] = {
            'proposal_id': winning_proposal_id,
            'member_name': winning_member.name,
            'votes_received': winning_votes,
            'proposal': winning_member.opinion
        }
        
        # The final decision IS the winning proposal verbatim
        results['final_decision'] = winning_member.opinion
        
        print(f"  Winner: PROPOSAL {winning_proposal_id} by {winning_member.name}")
        print(f"  Votes: {winning_votes}/{len(self.members)}")
        print(f"  Final Decision: {winning_member.opinion[:80]}...")
        print(f"\n{'='*60}")
        print("COUNCIL DELIBERATION CONCLUDED")
        print(f"{'='*60}\n")
        
        return results
    
    def format_results(self, results):
        """Format council results for display"""
        output = f"🏛️ **COUNCIL DELIBERATION RESULTS**\n\n"
        output += f"**Question:** {results['prompt']}\n\n"
        output += "---\n\n"
        
        output += "## Phase 1: Council Member Proposals\n\n"
        for member_data in results['members']:
            output += f"**PROPOSAL {member_data['proposal_id']}** by **{member_data['name']}** - *{member_data['role']}*\n"
            output += f"{member_data['proposal']}\n\n"
        
        output += "---\n\n"
        output += "## Phase 2: Deliberation & Analysis\n\n"
        output += f"{results['deliberation']}\n\n"
        
        output += "---\n\n"
        output += "## Phase 3: Council Votes (Each member distributes 5 votes to others)\n\n"
        
        # Calculate total votes per proposal first
        vote_totals = {}
        for vote_data in results['votes'].values():
            for proposal_id, votes in vote_data['distribution'].items():
                if votes > 0:
                    vote_totals[proposal_id] = vote_totals.get(proposal_id, 0) + votes
        
        # Show each proposal's vote count and who voted for it
        for proposal_id in range(len(results['members'])):
            proposal_member = results['members'][proposal_id]['name']
            total_votes = vote_totals.get(proposal_id, 0)
            
            output += f"**PROPOSAL {proposal_id}** by **{proposal_member}**: {total_votes} votes\n"
            
            # List who voted for this proposal and how many votes they gave
            voters = []
            for voter_name, vote_data in results['votes'].items():
                votes_given = vote_data['distribution'].get(proposal_id, 0)
                if votes_given > 0:
                    voters.append(f"{voter_name} ({votes_given})")
            
            if voters:
                output += f"  - Voted by: {', '.join(voters)}\n"
            else:
                output += f"  - No votes received\n"
            output += "\n"
        
        total_cast = sum(vote_totals.values())
        expected_total = len(results['members']) * 5  # Each member has 5 votes
        output += f"**Total Votes Cast:** {total_cast} votes (Expected: {expected_total})\n"
        
        if total_cast != expected_total:
            output += f"⚠️ *Warning: Vote count mismatch!*\n"
        
        output += "\n---\n\n"
        output += "## Phase 4: Winning Proposal\n\n"
        
        winner = results['winning_proposal']
        max_possible_votes = (len(results['members']) - 1) * 5  # 4 other members x 5 votes each = 20
        output += f"**WINNER:** PROPOSAL {winner['proposal_id']} by **{winner['member_name']}**\n"
        output += f"**Votes Received:** {winner['votes_received']} out of {max_possible_votes} possible votes\n\n"
        output += f"**Final Decision (Verbatim):**\n\n"
        output += f"*{results['final_decision']}*\n"
        
        return output

class ModelManager:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.use_quantization = True  # Enable quantization for speed
        self.past_key_values = None  # Cache for faster generation
        self.response_cache = ResponseCache(maxsize=100)
        self.web_searcher = WebSearcher()
        self.council = Council()
        self.warmed_up = False
        
    def load_model(self):
        """Load the model with optimizations"""
        if not MODEL_DIR.exists():
            raise FileNotFoundError(
                f"Model not found at {MODEL_DIR}. "
                "Please run 'python download_model.py' first."
            )
        
        print(f"Loading model from {MODEL_DIR}...")
        print(f"Using device: {self.device}")
        
        # Load tokenizer with fast option
        self.tokenizer = AutoTokenizer.from_pretrained(
            str(MODEL_DIR),
            trust_remote_code=True,
            use_fast=True  # Use fast tokenizer for speed
        )
        
        # Set padding token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model with CPU-optimized settings
        print("Loading with CPU-optimized settings...")
        
        # For CPU: Float32 is actually faster than BFloat16 on older CPUs
        # Only use BFloat16 if CPU supports it natively
        if self.device == "cpu":
            dtype = torch.float32  # Faster on most CPUs
            print("Using Float32 for CPU inference (faster)")
        else:
            dtype = torch.float16
            print("Using Float16 for GPU inference")
        
        try:
            # Try loading with optimizations
            self.model = AutoModelForCausalLM.from_pretrained(
                str(MODEL_DIR),
                trust_remote_code=True,
                torch_dtype=dtype,
                device_map="auto" if self.device == "cuda" else None,
                low_cpu_mem_usage=True,
                load_in_8bit=self.use_quantization and self.device == "cuda",
            )
        except Exception as e:
            print(f"Optimized loading failed, using defaults: {e}")
            self.model = AutoModelForCausalLM.from_pretrained(
                str(MODEL_DIR),
                trust_remote_code=True,
                low_cpu_mem_usage=True,
            )
        
        if self.device == "cpu" and self.model.device.type != "cpu":
            self.model = self.model.to(self.device)
        
        self.model.eval()
        
        # Enable PyTorch inference optimizations
        torch.set_num_threads(os.cpu_count())  # Use all CPU cores
        torch.set_grad_enabled(False)  # Disable gradients globally
        
        print("Model loaded successfully with optimizations!")
        
        # Warmup the model
        self._warmup()
    
    def _warmup(self):
        """Warmup model with a dummy forward pass"""
        if self.warmed_up:
            return
        
        print("Warming up model...")
        try:
            dummy_input = self.tokenizer(
                "Hello",
                return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                _ = self.model.generate(
                    dummy_input['input_ids'],
                    max_new_tokens=10,
                    do_sample=False
                )
            
            self.warmed_up = True
            print("Warmup complete!")
        except Exception as e:
            print(f"Warmup failed (non-critical): {e}")
        
    def generate_response(self, prompt, max_length=512, temperature=0.7, stream=False, web_search=False):
        """Generate a response from the model with optional web search"""
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Perform web search if enabled
        search_context = ""
        if web_search:
            results = self.web_searcher.search(prompt, max_results=3)
            if results:
                search_context = self.web_searcher.format_search_results(results)
                print(f"Added search context ({len(search_context)} chars)")
        
        # Check cache first (only for non-streaming and non-search)
        if not stream and not web_search:
            cached = self.response_cache.get(prompt, max_length, temperature)
            if cached is not None:
                print("Cache hit!")
                return cached
        
        # Format the prompt with search context if available
        if search_context:
            formatted_prompt = f"Context from web search:\n{search_context}\n\nUser question: {prompt}\n\nProvide a helpful answer based on the search results:\nOutput:"
        else:
            formatted_prompt = f"Instruct: {prompt}\nOutput:"
        
        # Tokenize input
        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=1024 if web_search else 512
        ).to(self.device)
        
        # Determine if we should use greedy decoding (faster)
        use_greedy = temperature < 0.3
        
        # Generate response
        with torch.no_grad():
            if stream:
                # Streaming generation
                streamer = self._stream_generate(inputs['input_ids'], max_length, temperature, use_greedy)
                return streamer
            else:
                # Regular generation with optimized parameters
                start_time = time.time()
                
                if use_greedy:
                    # Greedy decoding - much faster
                    outputs = self.model.generate(
                        inputs['input_ids'],
                        attention_mask=inputs.get('attention_mask'),
                        max_new_tokens=max_length,
                        do_sample=False,  # Greedy
                        pad_token_id=self.tokenizer.pad_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                        use_cache=True,
                        repetition_penalty=1.1,
                        early_stopping=True,
                        num_beams=1
                    )
                else:
                    # Sampling with temperature
                    outputs = self.model.generate(
                        inputs['input_ids'],
                        attention_mask=inputs.get('attention_mask'),
                        max_new_tokens=max_length,
                        temperature=temperature,
                        do_sample=True,
                        top_p=0.9,
                        top_k=50,
                        pad_token_id=self.tokenizer.pad_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                        use_cache=True,
                        repetition_penalty=1.1,
                        early_stopping=True
                    )
                
                response = self.tokenizer.decode(
                    outputs[0][inputs['input_ids'].shape[1]:],
                    skip_special_tokens=True
                ).strip()
                
                elapsed = time.time() - start_time
                tokens_generated = len(outputs[0]) - inputs['input_ids'].shape[1]
                print(f"Generated {tokens_generated} tokens in {elapsed:.2f}s ({tokens_generated/elapsed:.1f} tokens/s)")
                
                # Cache the response (only if not using web search)
                if not web_search:
                    self.response_cache.set(prompt, max_length, temperature, response)
                
                return response
    
    def _stream_generate(self, inputs, max_length, temperature, use_greedy=False):
        """Stream generation token by token with KV cache and early stopping"""
        past_key_values = None
        generated_tokens = 0
        consecutive_stops = 0
        
        for _ in range(max_length):
            with torch.no_grad():
                if past_key_values is None:
                    # First iteration - process full input
                    outputs = self.model(inputs, use_cache=True)
                    past_key_values = outputs.past_key_values
                else:
                    # Subsequent iterations - only process last token
                    outputs = self.model(inputs[:, -1:], past_key_values=past_key_values, use_cache=True)
                    past_key_values = outputs.past_key_values
                
                logits = outputs.logits[:, -1, :]
                
                if use_greedy:
                    # Greedy selection (faster)
                    next_token = torch.argmax(logits, dim=-1, keepdim=True)
                else:
                    # Sampling with temperature
                    logits = logits / temperature
                    probs = torch.softmax(logits, dim=-1)
                    next_token = torch.multinomial(probs, num_samples=1)
                
                # Check for end of sequence
                if next_token.item() == self.tokenizer.eos_token_id:
                    break
                
                # Decode token
                token_text = self.tokenizer.decode(next_token[0], skip_special_tokens=True)
                
                # Early stopping heuristics
                if token_text in ['.', '!', '?', '\n\n']:
                    consecutive_stops += 1
                    if consecutive_stops >= 2 and generated_tokens > 20:
                        # Stop if we've generated enough and hit multiple sentence endings
                        if token_text.strip():
                            yield token_text
                        break
                else:
                    consecutive_stops = 0
                
                if token_text.strip():  # Only yield non-empty tokens
                    yield token_text
                    generated_tokens += 1
                
                # Append token to inputs for next iteration
                inputs = torch.cat([inputs, next_token], dim=1)

# Initialize model manager
model_manager = ModelManager()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        data = request.json
        prompt = data.get('message', '')
        max_length = data.get('max_length', 512)
        temperature = data.get('temperature', 0.7)
        stream = data.get('stream', False)
        web_search = data.get('web_search', False)
        council_mode = data.get('council_mode', False)
        
        if not prompt:
            return jsonify({'error': 'No message provided'}), 400
        
        # Council mode takes precedence
        if council_mode:
            print("Activating Council Deliberation Mode...")
            council_results = model_manager.council.deliberate(prompt, model_manager)
            formatted_response = model_manager.council.format_results(council_results)
            return jsonify({
                'response': formatted_response,
                'council_results': council_results
            })
        
        if stream:
            def generate():
                for token in model_manager.generate_response(prompt, max_length, temperature, stream=True, web_search=web_search):
                    yield f"data: {json.dumps({'token': token})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            
            return Response(generate(), mimetype='text/event-stream')
        else:
            response = model_manager.generate_response(prompt, max_length, temperature, web_search=web_search)
            return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Check if model is loaded"""
    return jsonify({
        'loaded': model_manager.model is not None,
        'device': model_manager.device,
        'cache_size': len(model_manager.response_cache.cache),
        'warmed_up': model_manager.warmed_up
    })

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear response cache"""
    model_manager.response_cache.cache.clear()
    return jsonify({'status': 'Cache cleared'})

def main():
    """Main entry point"""
    print("=" * 60)
    print("DeepSeek R1 Local Web UI")
    print("=" * 60)
    
    # Load the model
    try:
        model_manager.load_model()
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease run: python download_model.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error loading model: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Starting web server...")
    print("=" * 60)
    print("\n✓ Server running at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()
