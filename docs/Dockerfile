FROM ruby:3.2

ENV LC_ALL C.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

WORKDIR /usr/src/app

# Copy both Gemfile and Gemfile.lock
COPY Gemfile Gemfile.lock ./

# Install Bundler and the bundle's gems
RUN gem install bundler && bundle install

EXPOSE 4000
CMD jekyll serve -d /_site --watch --force_polling -H 0.0.0.0 -P 4000
