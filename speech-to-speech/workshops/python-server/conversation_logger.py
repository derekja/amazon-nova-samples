import os
import json
from datetime import datetime
import threading

class ConversationLogger:
    """Logger for conversation text events with role distinction"""
    
    def __init__(self, log_file="conversation.log"):
        self.log_file = log_file
        self.lock = threading.Lock()
        self.content_tracker = {}  # Track content by contentId to avoid duplicates
        self.current_generation_stage = ""  # Track the most recent generation stage
        
    def log_event(self, event_data):
        """Log conversation events with role distinction and speculative/final marking"""
        try:
            if 'event' not in event_data:
                return
                
            event_name = list(event_data['event'].keys())[0]
            event_content = event_data['event'][event_name]
            
            if event_name == 'contentStart':
                # Track content start to get generation stage
                content_type = event_content.get('type', '')
                if content_type == 'TEXT':
                    role = event_content.get('role', 'UNKNOWN')
                    
                    # Extract generation stage from additionalModelFields and store it globally
                    if 'additionalModelFields' in event_content:
                        try:
                            additional_fields = json.loads(event_content['additionalModelFields'])
                            self.current_generation_stage = additional_fields.get('generationStage', '')
                        except Exception as e:
                            pass  # Ignore parsing errors
            
            elif event_name == 'textOutput':
                content_id = event_content.get('contentId', '')
                content = event_content.get('content', '')
                role = event_content.get('role', 'UNKNOWN')
                stop_reason = event_content.get('stopReason', '')
                
                # Update content tracker - use the current generation stage from the most recent contentStart
                if content_id not in self.content_tracker:
                    self.content_tracker[content_id] = {
                        'role': role,
                        'generation_stage': self.current_generation_stage,  # Use the current generation stage
                        'content': '',
                        'logged': False
                    }
                
                # Update the content
                self.content_tracker[content_id]['content'] = content
                self.content_tracker[content_id]['role'] = role
                
                # Log if there's substantial content and we haven't logged this contentId yet
                if content and content.strip() and len(content.strip()) > 5:
                    generation_stage = self.content_tracker[content_id]['generation_stage']
                    
                    # Use the generation stage from contentStart (like React client does)
                    # If no generation stage is set, use the React client logic:
                    # - Only show final content in the UI (commented line 472 shows stopReason filtering)
                    stage_marker = ""
                    if generation_stage:
                        # Use the actual generation stage from Nova Sonic
                        stage_marker = f" [{generation_stage}]"
                    else:
                        # Fallback: if no generation stage, determine from stop reason
                        # But this should rarely happen with proper Nova Sonic responses
                        if stop_reason in ['END_TURN', 'STOP_SEQUENCE', 'MAX_TOKENS']:
                            stage_marker = " [final]"
                        else:
                            # If no clear completion signal, likely speculative
                            stage_marker = " [speculative]"
                    
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Format role for display
                    role_display = {
                        'USER': '[USER]',
                        'ASSISTANT': '[ASSISTANT]',
                        'SYSTEM': '[SYSTEM]',
                        'TOOL': '[TOOL]'
                    }.get(role, f'[{role}]')
                    
                    log_entry = f"{timestamp} {role_display}{stage_marker}: {content}\n"
                    
                    # Write to log file with thread safety
                    with self.lock:
                        with open(self.log_file, 'a', encoding='utf-8') as f:
                            f.write(log_entry)
                            f.flush()  # Ensure immediate write
            
            elif event_name == 'contentEnd':
                # Mark content as ended
                content_type = event_content.get('type', '')
                if content_type == 'TEXT':
                    content_id = event_content.get('contentName', '')
                    if content_id in self.content_tracker:
                        self.content_tracker[content_id]['logged'] = True
                            
        except Exception as e:
            print(f"Error logging conversation: {e}")
            import traceback
            traceback.print_exc()
    
    def log_text_event(self, event_data):
        """Backward compatibility wrapper"""
        self.log_event(event_data)
    
    def log_session_start(self):
        """Log session start marker"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"\n{timestamp} [SESSION_START] New conversation session started\n"
            
            with self.lock:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
                    f.flush()
        except Exception as e:
            print(f"Error logging session start: {e}")
    
    def log_session_end(self):
        """Log session end marker"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"{timestamp} [SESSION_END] Conversation session ended\n"
            
            with self.lock:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
                    f.flush()
        except Exception as e:
            print(f"Error logging session end: {e}")
    
    def get_last_session_history(self):
        """Get chat history from the last session in the log file"""
        try:
            if not os.path.exists(self.log_file):
                return []
            
            chat_history = []
            current_session_messages = []
            
            with self.lock:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            
            # Process lines in reverse to find the most recent session
            in_last_session = False
            for line in reversed(lines):
                line = line.strip()
                if not line:
                    continue
                
                if '[SESSION_END]' in line:
                    in_last_session = True
                    continue
                elif '[SESSION_START]' in line:
                    if in_last_session:
                        break
                    continue
                
                if in_last_session:
                    # Parse the log line: timestamp [ROLE] [STAGE]: content
                    try:
                        # Find the role part: [USER], [ASSISTANT], etc.
                        role_start = line.find('[')
                        if role_start == -1:
                            continue
                        
                        role_end = line.find(']', role_start)
                        if role_end == -1:
                            continue
                        
                        # Skip timestamp
                        timestamp_end = line.find(' [')
                        if timestamp_end == -1:
                            continue
                        
                        role_part = line[timestamp_end + 1:role_end + 1]
                        
                        # Skip if this is a session marker
                        if 'SESSION_' in role_part:
                            continue
                        
                        # Extract role
                        role = role_part.strip('[]')
                        
                        # Find the content after the stage marker
                        content_start = line.find(': ', role_end)
                        if content_start == -1:
                            continue
                        
                        content = line[content_start + 2:]
                        
                        # Convert role format for S2S events
                        if role in ['USER', 'ASSISTANT', 'SYSTEM']:
                            current_session_messages.append({
                                'role': role,
                                'content': content
                            })
                    
                    except Exception as e:
                        print(f"Error parsing log line: {e}")
                        continue
            
            # Reverse to get chronological order and remove duplicates
            seen_content = set()
            for msg in reversed(current_session_messages):
                # Simple deduplication by content
                if msg['content'] not in seen_content:
                    chat_history.append(msg)
                    seen_content.add(msg['content'])
            
            return chat_history[:10]  # Limit to last 10 messages to avoid overwhelming context
            
        except Exception as e:
            print(f"Error reading chat history: {e}")
            return []