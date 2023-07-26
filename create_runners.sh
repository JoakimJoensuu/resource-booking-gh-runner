#!/bin/sh

set -eu

usage="$(basename "$0") [-h] [-o OWNER] [-r REPO] [-n RUNNERS]
where:
    -h  show this help text
    -o  GitHub repo owner
    -r  GitHub repo name
    -n  number of runners"

REPO=resource-booking-gh-runner
OWNER=JoakimJoensuu
RUNNERS_N=10

while getopts ':o:r:h:n:' option; do
  case "$option" in
  h)
    echo "$usage"
    exit
    ;;
  r) REPO=$OPTARG ;;
  o) OWNER=$OPTARG ;;
  n) RUNNERS_N=$OPTARG ;;
  :)
    printf "missing argument for -%s\n" "$OPTARG" >&2
    echo "$usage" >&2
    exit 1
    ;;
  \?)
    printf "illegal option: -%s\n" "$OPTARG" >&2
    echo "$usage" >&2
    exit 1
    ;;
  esac
done

mkdir -p actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.306.0.tar.gz --fail -L https://github.com/actions/runner/releases/download/v2.306.0/actions-runner-linux-x64-2.306.0.tar.gz
echo "b0a090336f0d0a439dac7505475a1fb822f61bbb36420c7b3b3fe6b1bdc4dbaa  actions-runner-linux-x64-2.306.0.tar.gz" | shasum -a 256 -c

start_runner() {

  RUNNER_NO=$1
  echo "Runner number $RUNNER_NO being set up"

  mkdir -p "$RUNNER_NO"

  tar xzf ./actions-runner-linux-x64-2.306.0.tar.gz --directory "$RUNNER_NO"

  cd "$RUNNER_NO"

  RESPONSE=$(gh api \
    --method POST \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "/repos/$OWNER/$REPO/actions/runners/registration-token")

  REGISTRATION_TOKEN=$(jq -n -r --argjson data "$RESPONSE" '$data.token')

  rm -f .runner

  ./config.sh --url "https://github.com/$OWNER/$REPO" --token "$REGISTRATION_TOKEN" --replace --unattended --name "runner_$RUNNER_NO"

  echo "Runner number $RUNNER_NO being started"

  CHILD_PID=""
  ./run.sh &
  CHILD_PID="$!"
  echo "Run script pid $CHILD_PID"

  wait
}

CHILD_PIDS=""

RUNNER_NO=0
while [ "$RUNNER_NO" -lt $RUNNERS_N ]; do

  start_runner $RUNNER_NO &

  CHILD_PIDS="$CHILD_PIDS $!"

  RUNNER_NO=$((RUNNER_NO + 1))
done

echo "This pid $$"
echo "All pids"
for PID in $CHILD_PIDS; do
  echo "$PID"
done

echo 'Kill everything with "pkill -TERM Runner.Listener"'

wait
