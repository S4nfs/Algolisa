/*
Technique - Classification 
Algorithm used - K-Nearest Neighbour (knn) "Birds of a feather flock together"

knn with one Intependent variable:
-Drop a ball bunch of times all around the board
-For each observation, subtract drop point from 300px, take absolute value
-Sort the results from least to greatest
-Look at the 'k' top records, What was the most common bucket?
-Whichever bucketcame up most frequently is the one ours will probably go into
*/

const output = [];
// let predictionPoint = 300;
// let k = 3;

// Ran every time a balls drops into a bucket
function onScoreUpdate(dropPosition, bounciness, size, bucketLabel) {
  output.push([dropPosition, bounciness, size, bucketLabel])
}


function runAnalysis() {
  const testSetSizeToBeCompared = 100
  const k = 10 //most optimal we get
  _.range(0, 3).forEach(feature => {    //passing only feature=1 dropposition, only feature=2 bounciness
    const data = _.map(output, row => [row[feature], _.last(row)])
    const [testSet, trainingSet] = splitDataSet(minMax(data, 1), testSetSizeToBeCompared)
    const accuracy = _.chain(testSet)
      .filter(testPoint => knn(trainingSet, _.initial(testPoint), k) === _.last(testPoint))
      .size()
      .divide(testSetSizeToBeCompared)
      .value()

    console.log('Accuracy: ', accuracy * 100, '% for Feature: ', feature)

    //===================OR=======================
    // let numberCorrect = 0
    // for (let i = 0; i < testSet.length; i++) {
    //   const bucket = knn(trainingSet, testSet[i][0], k)
    //   console.log(bucket, testSet[i][3])  //resulted bucket v/s expected bucket
    //   if (bucket === testSet[i][3]) {
    //     numberCorrect++
    //   }
    // }
    // console.log('Accuracy: ', (numberCorrect / testSetSizeToBeCompared) * 100, '% K: ', k)

  })


}

function knn(data, point, k) {
  //point has now 3 values
  return _.chain(data)
    .map(row => {
      return [distance(_.initial(row), point),
      _.last(row)]
    })
    .sortBy(row => row[0])
    .slice(0, k)
    .countBy(row => row[1])
    .toPairs()
    .sortBy(row => row[1])
    .last()
    .first()
    .parseInt()
    .value()
}

//3D Pythagorean theorem c2 = a2 + b2 | Getting Actual diagonal distance of hypotenuse  - (A(dropposition) ** 2 + B(Bounciness) ** 2 + C(Size) ** 2) ** 0.5
function distance(pointA, pointB) {
  return _.chain(pointA)
    .zip(pointB)
    .map(([a, b]) => (a - b) ** 2)
    .sum()
    .value() ** 0.5
}

//Getting Model Accuracy by comparing randomized training set and randomized test set data
function splitDataSet(data, testCount) {
  const shuffled = _.shuffle(data)
  const testSet = _.slice(shuffled, 0, testCount)   //upto testCount
  const trainingSet = _.slice(shuffled, testCount)  //rest of data
  return [testSet, trainingSet]
}

/* Data Set Normalization :
1.Normalised/scaling DataSet (range from 0 - 1)= Feature value - minOfFeatureValues / maxOfFeatureValues - minOfFeatureValues
2.Stardardized DataSet (beyond -1 - 1)
*/

//Normalizing data according to how many and putting back there
function minMax(data, featureCount) {
  const clonedData = _.cloneDeep(data)

  for (let i = 0; i < featureCount; i++) {
    const column = clonedData.map(row => row[i])
    const min = _.min(column)
    const max = _.max(column)

    for (let j = 0; j < clonedData.length; j++) {
      clonedData[j][i] = (clonedData[j][i] - min) / (max - min)
    }
  }
  return clonedData
}
