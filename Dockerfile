# bookworm ships GCC 12. Newer GCC (13/14+) turns the old-style C in these
# Lex/Yacc sources (implicit declarations, implicit int) into hard errors.
FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev flex bison libfl-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY compiler ./compiler
RUN mkdir -p bin

RUN cd compiler/lexical  && flex -o lex.yy.c scanner.l \
    && gcc lex.yy.c -w -lfl -o /app/bin/lexical
RUN cd compiler/syntax   && flex -o lex.yy.c lexicalAnalyzer.l && bison -y -d syntaxChecker.y \
    && gcc lex.yy.c y.tab.c -w -lfl -lm -o /app/bin/syntax
RUN cd compiler/semantic && flex -o lex.yy.c lexicalAnalyzer.l && bison -y -d syntaxChecker.y \
    && gcc lex.yy.c y.tab.c -w -lfl -lm -o /app/bin/semantic
RUN cd compiler/icg      && flex -o lex.yy.c lexicalAnalyzer.l && bison -y -d syntaxChecker.y \
    && gcc lex.yy.c y.tab.c icg.c -w -lfl -lm -o /app/bin/icg

COPY backend ./backend
COPY frontend ./frontend
RUN pip install --no-cache-dir -r backend/requirements.txt
ENV PORT=8000
CMD ["sh", "-c", "gunicorn -w 2 -b 0.0.0.0:${PORT} backend.app:app"]
