const gcp_sub_regions = [
  {
    name: 'US Central (Iowa)',
    code: 'us-central1',
    zones: ['us-central1-a', 'us-central1-b', 'us-central1-c', 'us-central1-f'],
  },
  {
    name: 'US East (South Carolina)',
    code: 'us-east1',
    zones: ['us-east1-b', 'us-east1-c', 'us-east1-d'],
  },
  {
    name: 'US East (Northern Virginia)',
    code: 'us-east4',
    zones: ['us-east4-a', 'us-east4-b', 'us-east4-c'],
  },
  {
    name: 'US West (Oregon)',
    code: 'us-west1',
    zones: ['us-west1-a', 'us-west1-b', 'us-west1-c'],
  },
  {
    name: 'US West (Los Angeles)',
    code: 'us-west2',
    zones: ['us-west2-a', 'us-west2-b', 'us-west2-c'],
  },
  {
    name: 'US West (Salt Lake City)',
    code: 'us-west3',
    zones: ['us-west3-a', 'us-west3-b', 'us-west3-c'],
  },
  {
    name: 'US West (Las Vegas)',
    code: 'us-west4',
    zones: ['us-west4-a', 'us-west4-b', 'us-west4-c'],
  },
  {
    name: 'Europe North (Finland)',
    code: 'europe-north1',
    zones: ['europe-north1-a', 'europe-north1-b', 'europe-north1-c'],
  },
  {
    name: 'Europe West (Belgium)',
    code: 'europe-west1',
    zones: ['europe-west1-b', 'europe-west1-c', 'europe-west1-d'],
  },
  {
    name: 'Europe West (London)',
    code: 'europe-west2',
    zones: ['europe-west2-a', 'europe-west2-b', 'europe-west2-c'],
  },
  {
    name: 'Europe West (Frankfurt)',
    code: 'europe-west3',
    zones: ['europe-west3-a', 'europe-west3-b', 'europe-west3-c'],
  },
  {
    name: 'Europe West (Netherlands)',
    code: 'europe-west4',
    zones: ['europe-west4-a', 'europe-west4-b', 'europe-west4-c'],
  },
  {
    name: 'Europe West (Zurich)',
    code: 'europe-west6',
    zones: ['europe-west6-a', 'europe-west6-b', 'europe-west6-c'],
  },
  {
    name: 'Asia South (Mumbai)',
    code: 'asia-south1',
    zones: ['asia-south1-a', 'asia-south1-b', 'asia-south1-c'],
  },
  {
    name: 'Asia Southeast (Singapore)',
    code: 'asia-southeast1',
    zones: ['asia-southeast1-a', 'asia-southeast1-b', 'asia-southeast1-c'],
  },
  {
    name: 'Asia East (Hong Kong)',
    code: 'asia-east2',
    zones: ['asia-east2-a', 'asia-east2-b', 'asia-east2-c'],
  },
  {
    name: 'Asia Northeast (Tokyo)',
    code: 'asia-northeast1',
    zones: ['asia-northeast1-a', 'asia-northeast1-b', 'asia-northeast1-c'],
  },
  {
    name: 'Asia Northeast (Osaka)',
    code: 'asia-northeast2',
    zones: ['asia-northeast2-a', 'asia-northeast2-b', 'asia-northeast2-c'],
  },
  {
    name: 'Asia Northeast (Seoul)',
    code: 'asia-northeast3',
    zones: ['asia-northeast3-a', 'asia-northeast3-b', 'asia-northeast3-c'],
  },
  {
    name: 'Australia Southeast (Sydney)',
    code: 'australia-southeast1',
    zones: ['australia-southeast1-a', 'australia-southeast1-b', 'australia-southeast1-c'],
  },
  {
    name: 'South America East (Sao Paulo)',
    code: 'southamerica-east1',
    zones: ['southamerica-east1-a', 'southamerica-east1-b', 'southamerica-east1-c'],
  },
]

// const zoneToInstanceIds = gcp_sub_regions.reduce((acc, { zones }) => {
//   zones.forEach((zone) => (acc[zone] = []))
//   return acc
// }, {})

const zoneToInstanceIds = gcp_sub_regions.reduce((acc, { code }) => {
  acc[code] = [] // Add the code as a key with an empty array
  return acc // Return the updated accumulator
}, {})
console.log(zoneToInstanceIds)

let role = 'Enterprise',
  permissionsError = false
if (role === 'Enterprise' && !permissionsError) {
  console.log('hhh')
}

const maxVal = (array) => {
  let m = array[0]
  for (let i = 0; i < array.length; i++) {
    if (array[i] > m) {
      m = array[i]
    }
  }
  return m
}

console.log(-10 > -10)
