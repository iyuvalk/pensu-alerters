{
  port: 8125,
  mgmt_port: 8126,

  percentThreshold: [99],

  graphitePort: 2003,
  graphiteHost: "127.0.0.1",
  flushInterval: 1000,
  deleteIdleStats: true,
  gaugesMaxTTL: 60,

  backends: ['./backends/graphite'],
  graphite: {
    legacyNamespace: false
  }
}