FROM golang:1.12.6-stretch

# 1. Create non-root user and group
RUN groupadd -g 999 go_user && useradd -r -u 999 -g go_user go_user

# 2. Create the working directory
RUN mkdir -p /home/go_user/app && chown -R go_user:go_user /home/go_user && chown -R go_user:go_user /home/go_user/app

# 3. Set the working directory
WORKDIR /home/go_user/app

# 4. Switch to non-root user
USER go_user

# 5. Copy the app into the working directory
COPY --chown=go_user:go_user . .

# 6. Fetch deps
# note: vendor or go get?
# RUN GO111MODULE=on go mod vendor
RUN GO111MODULE=on go get

# 7. Expose the ports
EXPOSE 8080
EXPOSE 3000
EXPOSE 3001

# 8. Run the app
CMD ["go", "run", "/home/go_user/app/cmd/host/main.go"]
