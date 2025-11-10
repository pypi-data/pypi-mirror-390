FROM golang:1.21-alpine AS builder

# Install Python and system dependencies needed for Typst
RUN apk add --no-cache python3 py3-pip wget xz-utils

WORKDIR /app

# Install Typst for PDF generation
RUN wget https://github.com/typst/typst/releases/download/v0.12.0/typst-x86_64-unknown-linux-musl.tar.xz && \
    tar -xf typst-x86_64-unknown-linux-musl.tar.xz && \
    mv typst-x86_64-unknown-linux-musl/typst /usr/local/bin/ && \
    chmod +x /usr/local/bin/typst && \
    rm -rf typst-x86_64-unknown-linux-musl*

# Copy Go mod files and download dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build the Go application
RUN go build -o main ./cmd/server

# Install rendercv Python package
RUN pip install "rendercv[full]"

# Final stage
FROM golang:1.21-alpine

# Install Python and system dependencies needed for Typst
RUN apk add --no-cache python3 py3-pip wget xz-utils

# Install Typst for PDF generation
RUN wget https://github.com/typst/typst/releases/download/v0.12.0/typst-x86_64-unknown-linux-musl.tar.xz && \
    tar -xf typst-x86_64-unknown-linux-musl.tar.xz && \
    mv typst-x86_64-unknown-linux-musl/typst /usr/local/bin/ && \
    chmod +x /usr/local/bin/typst && \
    rm -rf typst-x86_64-unknown-linux-musl*

# Copy the Go binary from the builder stage
COPY --from=builder /app/main .

# Install rendercv Python package
RUN pip install "rendercv[full]"

# Create directory for generated PDFs
RUN mkdir -p generated_pdfs

EXPOSE 5000

CMD ["./main"]