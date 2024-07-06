@@ -6,15 +6,18 @@
 
 import ai.assistant
 import ai.prompt
+import code.pull_request
 import config
-from app import App, get_pr, build_context
 import logger
+import review
+from app import App
 
 
 def main():
     try:
         cfg = config.from_env()
-        pr = get_pr(cfg.github)
+        pr = code.pull_request.get_pr(cfg.github)
+        logger.log.debug(f"Pull request retrieved: #{pr.number}")
     except github.GithubException as e:
         logger.log.critical(f"Couldn't retrieve pull request from Github: {e}")
         sys.exit(69)
@@ -23,7 +26,8 @@ def main():
         sys.exit(42)
 
     try:
-        context = build_context(pr)
+        context = review.build_context(pr)
+        logger.log.debug(f"Context built successfully: {context.title}")
         builder = ai.prompt.Builder(context)
         assistant = ai.assistant.Assistant(cfg.llm.model, builder)
