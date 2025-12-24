/*
Technique - Regression 
Features -  longtitude/latitudes
labels - House price
Algorithm used - K-Nearest Neighbour (knn) "Birds of a feather flock together"

knn with one Intependent variable:
-Find distance between features (longtitude/latitudes of existing houses) and prediction points (longtitude/latitudes of new house)
Distance =  √(lat - lot)2 + (long - long)2
-Sort from lowest to greatest
-Look at the 'k' top records
-Average the label value of those top K records



Demo:
const features = tf.tensor([
    [-150, 20.0],
    [-151.5, 25.5],
    [-152.9, 28.9]
])

const labels = tf.tensor([
    [200],
    [220],
    [199]
])

const k = 2
const predictionPoint = tf.tensor([-150, 24])
features
    .sub(predictionPoint)
    .pow(2)
    .sum(1)
    .pow(0.5)
    .expandDims(1)
    .concat(labels, 1)
    .unstack()
.sort((a,b) => a.get(0) > b.get(0) ? 1 : -1)
.slice(0, k)
.reduce((acc, pair) => acc + pair.get(1), 0)/k

*/
require("@tensorflow/tfjs-node")
const tf = require("@tensorflow/tfjs")
const loadCSV = require('./load-csv')

function knn(features, labels, predictionPoint, k) {
    /* Data Set Normalization :
    1.Normalised/scaling DataSet (range from 0 - 1)= Feature value - minOfFeatureValues / maxOfFeatureValues - minOfFeatureValues
    2.Stardardized DataSet (beyond -1 - 1) = Value - Average(aka mean) / standard deviation (aka. sqrt(variance)
    */
    //applying standardization here
    const { mean, variance } = tf.moments(features, 0)
    const scaledPrediction = predictionPoint.sub(mean).div(variance.pow(0.5))

    return features
        .sub(mean)
        .div(variance.pow(0.5))
        .sub(scaledPrediction)
        .pow(2)
        .sum(1)
        .pow(0.5)
        .expandDims(1)
        .concat(labels, 1)
        .unstack()
        .sort((a, b) => a.arraySync()[0] > b.arraySync()[0] ? 1 : -1)
        .slice(0, k)
        .reduce((acc, pair) => acc + pair.arraySync()[1], 0) / k
}
let { features, labels, testFeatures, testLabels } = loadCSV('kc_house_data.csv', {
    shuffle: true,
    splitTest: 10,
    dataColumns: ['lat', 'long'],
    labelColumns: ['price']
}) //remember all are 2D arrays

// console.log(testLabels[0][0])
// console.log(testFeatures[0])

features = tf.tensor(features)
labels = tf.tensor(labels)

testFeatures.forEach((testpoint, i) => {   //iterating all the 10 testfeatures and testLabels instead of hardcoded single value like [ 47.561, -122.226 ]

    const result = knn(features, labels, tf.tensor(testpoint), 10)
    //error = expected value - predicted value / expected value
    const err = (testLabels[i][0] - result) / testLabels[i][0]
    console.log("Result", result, testLabels[0][0], "Error", err * 100)
})

