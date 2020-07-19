FROM cypress/browsers:node13.6.0-chrome80-ff72

# label and environment variables
LABEL maintainer="engineering@digitaled.com"
ENV CYPRESS /cypress-testing

# setup the working folder and copy the files
RUN mkdir ${CYPRESS}
WORKDIR ${CYPRESS}
COPY cypress ./cypress
COPY cypress.json .
COPY package.json .
COPY package-lock.json .
COPY tsconfig.json .
COPY webpack.config.js .

# Copy NPM & Install
RUN CI=true npm install
RUN CI=true node_modules/.bin/cypress install

# setup the script that will run the tests
COPY buildScripts/run.sh /
RUN chmod 777 /run.sh


# Run tests
CMD ["/run.sh"]
